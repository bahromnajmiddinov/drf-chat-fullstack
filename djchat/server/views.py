"""
API endpoint for listing server objects.

This viewset provides functionalities to filter and retrieve server objects
based on various query parameters.

**Permissions:**
* Filtering by user membership (`by_user=true`) requires user authentication.

**Query Parameters:**
* category (str, optional): Filter servers by category name.
* qty (int, optional): Limit the number of returned servers.
* by_user (bool, optional): Filter servers for the requesting user (requires authentication).
* by_serverid (int, optional): Retrieve a single server by its ID.
* with_num_members (bool, optional): Include the number of members for each server in the response.

**Raises:**
* `AuthenticationFailed`: If user tries to access user-specific filters without being authenticated.
* `ValidationError`:
    * If server with requested ID is not found (`by_serverid`).
    * If invalid value is provided for `qty`.
"""

# from django.shortcuts import get_object_or_404
from django.db.models import Count

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from .serializers import ServerSerializer
from .models import Server
from .schema import server_list_docs


class ServerListViewSet(ViewSet):
    """
    ViewSet for listing server objects.
    """

    queryset = Server.objects.all()
    """
    Queryset containing all server objects.
    """

    @server_list_docs
    def list(self, request):
        """
        List servers based on optional query parameters.

        Args:
            request (HttpRequest): The request object containing query parameters.

        Returns:
            Response: A response containing serialized server data.

        Raises:
            AuthenticationFailed: If the user is not authenticated and tries to filter by user or server ID.

            ValidationError: If server with the specified ID does not exist, or if there's a value error.

        Examples:
            # List all servers
            /api/servers/

            # List servers in a specific category
            /api/servers/?category=gaming

            # List servers with the number of members included
            /api/servers/?with_num_members=true

            # List servers created by the authenticated user
            /api/servers/?by_user=true (Requires authentication)

            # List a specific server by ID
            /api/servers/?by_serverid=1234
        """

        category = request.query_params.get('category')
        qty = request.query_params.get('qty')
        by_user = request.query_params.get('by_user') == 'true'
        by_serverid = request.query_params.get('by_serverid')
        with_num_members = request.query_params.get('with_num_members') == 'true'

        # Check user authentication for specific requests
        # if by_user or by_serverid and not request.user.is_authenticated:
        #     raise AuthenticationFailed()

        # Filter by category
        if category:
            self.queryset = self.queryset.filter(category__name=category)

        # Filter by user membership (if authenticated)
        if by_user:
            if by_user and request.user.is_authenticated:
                user_id = request.user.id
                self.queryset = self.queryset.filter(member=user_id)
            else:
                raise AuthenticationFailed()

        # Annotate queryset with number of members (if requested)
        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count('members'))

        # Filter by server ID (handle errors)
        if by_serverid:
            if not request.user.is_authenticated:
                raise AuthenticationFailed()
            
            try:
                self.queryset = self.queryset.filter(id=by_serverid)
                if not self.queryset.exists():
                    raise ValidationError(detail=f'Server with id {by_serverid} not found')
            except ValueError:
                raise ValidationError(detail='Value error')

        # Limit results by quantity
        if qty:
            self.queryset = self.queryset[:int(qty)]
            
        # Serialize the queryset and return the response
        serializer = ServerSerializer(self.queryset, many=True, context={'num_members': with_num_members})
        return Response(serializer.data)
