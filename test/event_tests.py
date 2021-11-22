from django.http import response
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from levelupapi.models import GameType, Game, Gamer, Event

class EventTests(APITestCase):
    def setUp(self):
        """
        Create a new Gamer, collect the auth Token, and create a sample GameType
        """

        # Define the URL path for registering a Gamer
        url = '/register'

        # Define the Gamer properties
        gamer = {
            "username": "steve",
            "password": "Admin8*",
            "email": "steve@stevebrownlee.com",
            "address": "100 Infinity Way",
            "phone_number": "555-1212",
            "first_name": "Steve",
            "last_name": "Brownlee",
            "bio": "Love those gamez!!"
        }

        # Initiate POST request and capture the response
        response = self.client.post(url, gamer, format='json')

        # Store the TOKEN from the response data
        self.token = Token.objects.get(pk=response.data['token'])

        # Use the TOKEN to authenticate the requests
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Assert that the response status code is 201 (CREATED)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # SEED THE DATABASE WITH A GAMETYPE
        # This is necessary because the API does not
        # expose a /gametypes URL path for creating GameTypes

        # Create a new instance of GameType
        game_type = GameType()
        game_type.label = "Board game"
        # Save the GameType to the testing database
        game_type.save()
        self.game = Game.objects.create(
            game_type = game_type,
            title = "Battleship",
            maker = "Hasbro",
            gamer_id = 1,
            num_of_players = 4,
            skill_level=2
        )

    
    def test_create_event(self):
        event = {
            "date": "2021-11-24",
            "time": "8:00",
            "description": "Battleship Game",
            "game": self.game.id   
        }
        response = self.client.post('/events', event, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['date'], event['date'])
        self.assertEqual(response.data['time'], event['time'])
        self.assertEqual(response.data['description'], event['description'])
        self.assertEqual(response.data['organizer']['id'], 1)
    
    def test_get_event(self):
        event = Event()
        event.organizer_id = 1
        event.game_id = 1
        event.description = "Battleship Game"
        event.date = "2021-11-25"
        event.time = "18:00:00"
        
        event.save()
        
        url = f'/events/{event.id}'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['date'], event.date)
        self.assertEqual(response.data['time'], event.time)
        self.assertEqual(response.data['description'], event.description)
        self.assertEqual(response.data['organizer']['id'], 1)
        
        
    def test_change_event(self):
        event = Event()
        event.organizer_id = 1
        event.game_id = 1
        event.description = "Battleship Game"
        event.date = "2021-11-25"
        event.time = "18:00:00"
        
        event.save()
        
        url = f'/events/{event.id}'
        
        new_event = {
            "date": "2021-11-24",
            "time": "08:00:00",
            "description": "Battleship Game",
            "gameId": 1
        }
        
        response = self.client.put(url, new_event, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['date'], new_event['date'])
        self.assertEqual(response.data['time'], new_event['time'])
        self.assertEqual(response.data['description'], new_event['description'])
        self.assertEqual(response.data['organizer']['id'], 1)
    
    def test_delete_event(self):
        
        event = Event()
        event.organizer_id = 1
        event.game_id = 1
        event.description = "Battleship Game"
        event.date = "2021-11-25"
        event.time = "18:00:00"
        
        event.save()
        
        url = f'/events/{event.id}'
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        
        