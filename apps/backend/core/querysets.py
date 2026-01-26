class ScopeQuerySetMixin:
    """
    Automatically filters the queryset based on the scope
    """

    owner_type_field = "owner_type"
    owner_id_field = "owner_id"

    def get_queryset(self):
        scope = getattr(self.request, "scope", None)

        if scope is None:
            return self.queryset.none()
        
        return self.queryset.filter(
            **{
                self.owner_type_field: scope.owner_type,
                self.owner_id_field: scope.owner_id
            }
        )