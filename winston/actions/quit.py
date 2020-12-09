""" :quit
"""
import logging
from . import _actions as actions
from ..app import App
from ..ui import Interaction


@actions.register
class Action:
    """handle :quit"""

    # pylint: disable=too-few-public-methods

    KEGEX = r"q(?:uit)?(?P<exclamation>!)?$"

    def __init__(self):
        self._logger = logging.getLogger()

    # pylint: disable=unused-argument
    def run(self, interaction: Interaction, app: App) -> Interaction:
        """Handle :doc

        :param interaction: The interaction from the user
        :type interaction: Interaction
        :param app: The app instance
        :type app: App
        """
        # : quit will be handled in the app
        self._logger("quit was requested as: %s", interaction.action.value)
        return interaction
