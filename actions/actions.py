from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, utils
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase
from rasa_sdk.executor import CollectingDispatcher
import os

from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase

USE_NEO4J = bool(os.getenv("USE_NEO4J", False))

if USE_NEO4J:
    from neo4j_knowledge_base import Neo4jKnowledgeBase


class MyKnowledgeBaseAction(ActionQueryKnowledgeBase):

    def name(self) -> Text:
        return "action_response_query"

    def __init__(self):
        if USE_NEO4J:
            print("using Neo4jKnowledgeBase")
            knowledge_base = Neo4jKnowledgeBase(
                "bolt://localhost:7687", "neo4j", "43215678"
            )
        else:
            print("using InMemoryKnowledgeBase")
            knowledge_base = InMemoryKnowledgeBase("data.json")

        super().__init__(knowledge_base)

    async def utter_objects(
        self,
        dispatcher: CollectingDispatcher,
        object_type: Text,
        objects: List[Dict[Text, Any]],
    ) -> None:
        """
        Utters a response to the user that lists all found objects.
        :param dispatcher: the dispatcher
        :param object_type: the object type
        :param objects: the list of objects
        :return: None
        """

        if objects:
            dispatcher.utter_message(text=f"Found the following {object_type}s:")

            repr_function = await utils.call_potential_coroutine(
                self.knowledge_base.get_representation_function_of_object(object_type)
            )

            for i, obj in enumerate(objects, 1):
                dispatcher.utter_message(text=f"{i}: {repr_function(obj)}")
        else:
            dispatcher.utter_message(text=f"I did not find any {object_type}s.")

    def utter_attribute_value(
        self,
        dispatcher: CollectingDispatcher,
        object_name: Text,
        attribute_name: Text,
        attribute_value: Text,
    ) -> None:
        """
        Utters a response that informs the user about the attribute value of the
        attribute of interest.
        :param dispatcher: the dispatcher
        :param object_name: the name of the object
        :param attribute_name: the name of the attribute
        :param attribute_value: the value of the attribute
        :return: None
        """

        if attribute_value:
            dispatcher.utter_message(text=f"The {attribute_name} of {object_name} is {attribute_value}.")
        else:
            dispatcher.utter_message(text=f"I didn't find the {attribute_name} of {object_name}.")
