from rest_framework import mixins, viewsets


class ListCreateDestroyViewSet(mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    """
    A viewset that provides default `create()`, `destroy()`, `list()` actions.
    """
    pass
