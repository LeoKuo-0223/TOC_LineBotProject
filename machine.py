from fsm import TocMachine


def create_machine():
    machine = TocMachine(
        states=["user", "dict", "checkWord", "findWord", "tmpFindWord", "tmpCheckWord"],
        transitions=[
            {
                "trigger": "advance",
                "source": "user",
                "dest": "dict",
                "conditions": "is_going_to_dict",
            },
            {
                "trigger": "advance", 
                "source": "dict", 
                "dest": "findWord",
            },
            {
                "trigger": "advance", 
                "source": "findWord",
                "dest": "checkWord",
                "conditions": "is_going_to_checkWord"
            },
            {
                "trigger": "advance", 
                "source": "findWord",
                "dest": "tmpFindWord",
                # "conditions": "is_going_to_tmpFindWord"
            },
            {
                "trigger": "advance",
                "source": "checkWord",
                "dest": "tmpCheckWord", 
                "conditions": "is_going_to_tmpCheckWord"
            },
            {
                "trigger": "go_back", 
                "source": ["checkWord","findWord", "tmpFindWord"],
                "dest": "dict",
            },
            {
                "trigger": "go_back_user", 
                "source": "findWord",
                "dest": "user",
            },
            {
                "trigger": "go_back_findWord",
                "source": ["tmpFindWord", "tmpCheckWord"],
                "dest": "findWord"
            },
            {
                "trigger": "go_back_checkWord",
                "source": "tmpCheckWord",
                "dest": "checkWord",
            },
            
        ],

        initial="user",
        auto_transitions=False,
        show_conditions=True,
    )
    return machine