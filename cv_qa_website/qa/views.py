# views.py

from typing import Any
from django.shortcuts import render
from django.http import JsonResponse
from .chatbot import ChatBotProcess
from .utils.bot_utils import (
    Configuration,
    ChatOpenAIManagement,
)
from django.views import View
from .models import Message
from django.views.decorators.csrf import csrf_protect
import json
import pickle


@csrf_protect
def home_view(request):
    return render(request, "index.html")


def terms_and_policies_view(request):
    return render(request, "terms_and_policies.html")


class ChatEndpointView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode("utf-8"))
        message = data.get("message")
        # check that mesage is smaller than 255 characters
        if len(message) > 100:
            message = message[:100]

        if not message:
            response = "Please enter a question."
        else:
            chatbot_serialized = request.session.get("chatbot")
            if not chatbot_serialized:
                config = Configuration("config.json")
                chatbot = ChatBotProcess(config, ChatOpenAIManagement)
            else:
                chatbot = pickle.loads(chatbot_serialized)
            response = chatbot.execute_answer(message)
            request.session["chatbot"] = pickle.dumps(chatbot)

        to_save = Message(content=message, answer=response)
        to_save.save()

        return JsonResponse({"response": response})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"error": "Only POST method allowed."})
