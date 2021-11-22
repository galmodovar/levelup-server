"""View module for handling requests about games"""
from django.core.exceptions import ValidationError
from django.db.models.aggregates import Count
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers, status
from levelupapi.models import Event, EventGamer, Game, Gamer
from django.contrib.auth.models import User


class EventView(ViewSet):
    """Level up events"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized event instance
        """

        # Uses the token passed in the `Authorization` header
        gamer = Gamer.objects.get(user=request.auth.user)

        event = Event()
        event.description = request.data["description"]
        event.time = request.data["time"]
        event.date = request.data["date"]
        event.organizer = gamer

        game = Game.objects.get(pk=request.data["game"])
        event.game = game


        # Try to save the new game to the database, then
        # serialize the game instance as JSON, and send the
        # JSON as a response to the client request
        try:
            # Create a new Python instance of the Game class
            # and set its properties from what was sent in the
            # body of the request from the client.
            event.save()
            serializer = EventSerializer(event, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # If anything went wrong, catch the exception and
        # send a response with a 400 status code to tell the
        # client that something was wrong with its request data
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)



    def retrieve(self, request, pk=None):
        """Handle GET requests for single game

        Returns:
            Response -- JSON serialized game instance
        """
        try:
            # `pk` is a parameter to this function, and
            # Django parses it from the URL route parameter
            #   http://localhost:8000/games/2
            #
            # The `2` at the end of the route becomes `pk`
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """Handle PUT requests for a game

        Returns:
            Response -- Empty body with 204 status code
        """
        organizer = Gamer.objects.get(user=request.auth.user)

 
        event = Event.objects.get(pk=pk)
        event.description = request.data["description"]
        event.date = request.data["date"]
        event.time = request.data["time"]
        event.organizer = organizer
        game = Game.objects.get(pk=request.data["gameId"])
        event.game = game
        event.save()

        # 204 status code means everything worked but the
        # server is not sending back any data in the response
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single event

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            event = Event.objects.get(pk=pk)
            event.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Event.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to games resource

        Returns:
            Response -- JSON serialized list of games
        """
        # Get current authenticated user
        gamer = Gamer.objects.get(user=request.auth.user)
        events = Event.objects.all()

        events = Event.objects.annotate(
            attendees_count = Count('attendees'),
            joined=Count('attendees')
        )

        # Support filtering events by game
        game = self.request.query_params.get('gameId', None)
        if game is not None:
            events = events.filter(game__id=type)

        serializer = EventSerializer(
            events, many=True, context={'request': request})
        return Response(serializer.data)
    
    
    @action(methods=['post', 'delete'], detail=True)
    def signup(self, request, pk=None):
        """Managing gamers signing up for events"""
        # Django uses the `Authorization` header to determine
        # which user is making the request to sign up
        gamer = Gamer.objects.get(user=request.auth.user)

        try:
            # Handle the case if the client specifies a game
            # that doesn't exist
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response(
                {'message': 'Event does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # A gamer wants to sign up for an event
        if request.method == "POST":
            try:
                # Using the attendees field on the event makes it simple to add a gamer to the event
                # .add(gamer) will insert into the join table a new row the gamer_id and the event_id
                event.attendees.add(gamer)
                return Response({}, status=status.HTTP_201_CREATED)
            except Exception as ex:
                return Response({'message': ex.args[0]})

        # User wants to leave a previously joined event
        elif request.method == "DELETE":
            try:
                # The many to many relationship has a .remove method that removes the gamer from the attendees list
                # The method deletes the row in the join table that has the gamer_id and event_id
                event.attendees.remove(gamer)
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            except Exception as ex:
                return Response({'message': ex.args[0]})


class UserSerializer(serializers.ModelSerializer):
    """JSON serializer for Django user (organizer)"""
    class Meta:
        model = User
        fields = ( 'id', 'first_name', 'last_name', 'email')

class GamerSerializer(serializers.ModelSerializer):
    """JSON serializer for event organizer"""
    user = UserSerializer()
    class Meta:
        model = Gamer
        fields = ('id', 'user',)


class GameSerializer(serializers.ModelSerializer):
    """JSON serializer for games"""

    class Meta:
        model = Game
        fields = ('id', 'title', 'maker', 'num_of_players', 'skill_level', 'game_type', 'gamer')

class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for events"""
    organizer = GamerSerializer(many=False)
    game = GameSerializer(many=False)
    joined = serializers.BooleanField(required=False)
    attendees_count = serializers.IntegerField(default=None)
    class Meta:
        model = Event
        fields = ('id', 'game', 'organizer', 'description', 'date', 'time', 'joined', 'attendees_count')
        depth = 1