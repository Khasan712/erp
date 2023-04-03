from rest_framework import serializers

from api.v1.reports.models import Report


class ReportGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('id', 'done_by', 'report_file', 'created_at')

    def to_representation(self, instance):
        res = super().to_representation(instance)
        if res.get("done_by"):
            res['done_by'] = {
                'id': instance.done_by.id,
                'first_name': instance.done_by.first_name,
                'last_name': instance.done_by.last_name,
            }
        return res
