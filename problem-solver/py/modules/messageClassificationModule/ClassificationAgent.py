"""
This code creates some test agent and registers until the user stops the process.
For this we wait for SIGINT.
"""
import logging
from sc_client.models import ScAddr, ScLinkContentType, ScTemplate
from sc_client.constants import sc_types
from sc_client.client import template_search
import json
from sc_kpm import ScAgentClassic, ScModule, ScResult, ScServer
from sc_kpm.sc_sets import ScSet
from sc_kpm.utils import (
    create_link,
    get_link_content_data,
    check_edge, create_edge,
    delete_edges,
    get_element_by_role_relation,
    get_element_by_norole_relation,
    get_system_idtf,
    get_edge
)
from sc_kpm.utils.action_utils import (
    create_action_answer,
    finish_action_with_status,
    get_action_arguments,
    get_element_by_role_relation
)
from sc_kpm import ScKeynodes

import requests


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)


class ClassificationAgent(ScAgentClassic):
    def __init__(self):
        super().__init__("action_rasa_classificate")

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        result = self.run(action_element)
        is_successful = result == ScResult.OK
        finish_action_with_status(action_element, is_successful)
        self.logger.info("ClassificationAgent finished %s",
                         "successfully" if is_successful else "unsuccessfully")
        return result

    def run(self, action_node: ScAddr) -> ScResult:
        self.logger.info("ClassificationAgent started")
        message_addr = get_action_arguments(action_node, 1)[0]
        message = self.get_message_text(message_addr)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = '{ "text":"' + message + '"}'
        response = requests.post(
            'http://localhost:5005/model/parse', headers=headers, data=data)
        classificated = response.json()
        self.logger.info(json.dumps(classificated, indent=4))

        return ScResult.OK

    def get_message_text(self, message_addr):
        nrel_translation = ScKeynodes.resolve(
            "nrel_sc_text_translation", sc_types.NODE_ROLE)

        template = ScTemplate()
        template.triple_with_relation(
            sc_types.NODE,
            sc_types.EDGE_D_COMMON_VAR,
            message_addr,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            nrel_translation
        )
        search_results = template_search(template)
        translation_node = ScSet(set_node=search_results[0][0])

        message_link = list(translation_node.elements_set)[0]
        return get_link_content_data(message_link)
