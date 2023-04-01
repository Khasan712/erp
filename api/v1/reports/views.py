from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from api.v1.contracts.models import Contract

from api.v1.reports.to_exel import contract_to_exel


class ReportAPi(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_contract_queryset(self):
        return Contract.objects.select_related(
            'parent_agreement', 'departement', 'category', 'currency', 'organization', 'create_by', 'supplier'
        ).filter(
            organization_id=self.request.user.organization.id
        )

    def post(self, request):
        try:
            request_data = request.data
            method = request_data.get('method')
            if not method or method not in ('contract.to.exel',):
                raise ValueError("Method not given or not found!")
            match method:
                case 'contract.to.exel':
                    """ Write contract data to exel """
                    return Response({
                        "success": True,
                        "file": contract_to_exel(self.request)
                    })
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            })

