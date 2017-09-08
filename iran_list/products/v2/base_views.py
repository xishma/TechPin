from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from .response import ApiResponse


class GenericView:
    model_name = 'object'
    message = {'update': None, 'destroy': None, 'list': None, 'create': None, 'retrieve': None}
    set_user = False


class UpdateView(GenericView, generics.UpdateAPIView):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if self.set_user:
            serializer.user = request.user

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(ApiResponse.get_base_response(data={self.model_name: serializer.data},
                                                      message=self.message['update']))


class DestroyView(GenericView, generics.DestroyAPIView):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(ApiResponse.get_base_response(message=self.message['destroy']))


class ListView(GenericView, generics.ListAPIView):
    # pagination_class = DefaultPaginator

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response['%ss' % self.model_name] = response.pop('results', [])
            response_data = ApiResponse.get_base_response(data=response, message=self.message['list'])
        else:
            serializer = self.get_serializer(queryset, many=True)
            response_data = ApiResponse.get_base_response(data={'%ss' % self.model_name: serializer.data, },
                                                          message=self.message['list'])

        return Response(response_data)


class CreateView(GenericView, generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if self.set_user:
            serializer.user = request.user

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(ApiResponse.get_base_response(response_code=status.HTTP_201_CREATED,
                                                      data={self.model_name: serializer.data},
                                                      message=self.message['create']),
                        status=status.HTTP_201_CREATED, headers=headers)


class RetrieveView(GenericView, generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            ApiResponse.get_base_response(data={self.model_name: serializer.data}, message=self.message['retrieve']))
