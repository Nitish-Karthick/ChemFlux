import io
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Dataset
from .serializers import DatasetSerializer


class PingView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({'status': 'ok', 'time': timezone.now()})


class UploadCSVView(APIView):
    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'detail': 'No file provided. Use key "file".'}, status=400)
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            return Response({'detail': f'Invalid CSV: {e}'}, status=400)

        df.columns = [c.strip() for c in df.columns]
        total_count = int(len(df))

        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        averages = {col: round(float(df[col].mean()), 2) for col in numeric_cols}

        type_col = None
        for candidate in ['Type', 'type', 'Equipment Type', 'equipment_type']:
            if candidate in df.columns:
                type_col = candidate
                break
        if type_col:
            type_dist = df[type_col].astype(str).value_counts(dropna=False).to_dict()
        else:
            type_dist = {}

        preview_rows = df.head(10).to_dict(orient='records')

        summary = {
            'total_count': total_count,
            'averages': averages,
            'type_distribution': type_dist,
            'columns': df.columns.tolist(),
            'preview': preview_rows,
        }

        dataset = Dataset.objects.create(
            name=getattr(uploaded_file, 'name', f'dataset_{timezone.now().isoformat()}'),
            csv_file=uploaded_file,
            summary=summary,
        )

        ids_to_keep = list(Dataset.objects.order_by('-uploaded_at').values_list('id', flat=True)[:5])
        if len(ids_to_keep) >= 5:
            Dataset.objects.exclude(id__in=ids_to_keep).delete()

        return Response(DatasetSerializer(dataset).data, status=status.HTTP_201_CREATED)


class DatasetListView(APIView):
    def get(self, request):
        datasets = Dataset.objects.order_by('-uploaded_at')[:5]
        data = DatasetSerializer(datasets, many=True).data
        return Response({'count': len(data), 'results': data})


class DatasetDetailView(APIView):
    def get(self, request, pk):
        dataset = get_object_or_404(Dataset, pk=pk)
        return Response(DatasetSerializer(dataset).data)


class DatasetReportView(APIView):
    def get(self, request, pk):
        dataset = get_object_or_404(Dataset, pk=pk)

        buf = io.BytesIO()
        p = canvas.Canvas(buf, pagesize=A4)
        width, height = A4

        y = height - 50
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y, "ChemFlux Report")
        y -= 25

        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"Dataset: {dataset.name}")
        y -= 15
        p.drawString(50, y, f"Uploaded At: {dataset.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}")
        y -= 25

        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Summary")
        y -= 18
        p.setFont("Helvetica", 10)
        summary = dataset.summary or {}
        p.drawString(50, y, f"Total Count: {summary.get('total_count', 0)}")
        y -= 15

        averages = summary.get('averages', {})
        p.drawString(50, y, "Averages:")
        y -= 15
        for k, v in averages.items():
            p.drawString(70, y, f"- {k}: {v}")
            y -= 14
            if y < 80:
                p.showPage()
                y = height - 50
                p.setFont("Helvetica", 10)

        type_dist = summary.get('type_distribution', {})
        p.drawString(50, y, "Type Distribution:")
        y -= 15
        for k, v in type_dist.items():
            p.drawString(70, y, f"- {k}: {v}")
            y -= 14
            if y < 80:
                p.showPage()
                y = height - 50
                p.setFont("Helvetica", 10)

        p.showPage()
        p.save()
        pdf = buf.getvalue()
        buf.close()

        resp = HttpResponse(pdf, content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="chemflux_report_{dataset.id}.pdf"'
        return resp
