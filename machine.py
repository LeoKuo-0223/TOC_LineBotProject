from fsm import TocMachine


def create_machine():
    machine = TocMachine(
        states=["user", "dict", "checkWord", "findWord", "tmpFindWord",
         "tmpCheckWord", "jisho", "findTanngo", "showFsm", "greet", "intro"
         ],
        transitions=[
            {
                "trigger": "advance",
                "source": ["user", "greet"],
                "dest": "dict",
                "conditions": "is_going_to_dict",
            },
            {
                "trigger": "advance",
                "source": "user",
                "dest": "greet",
                "conditions": "is_going_to_greet",
            },
            {
                "trigger": "advance",
                "source": "greet",
                "dest": "intro",
                "conditions": "is_going_to_intro",
            },
            {
                "trigger": "advance",
                "source": "user",
                "dest": "showFsm",
                "conditions": "is_going_to_showFsm"
            },
            {
                "trigger": "advance",
                "source": ["user", "greet"],
                "dest": "jisho",
                "conditions": "is_going_to_jisho",
            },
            {
                "trigger": "advance", 
                "source": "dict", 
                "dest": "findWord",
            },
            {
                "trigger": "advance", 
                "source": "jisho", 
                "dest": "findTanngo",
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
                "source": "findTanngo",
                "dest": "findTanngo",
                "conditions": "is_findTanngo_again"
            },
            {
                "trigger": "advance",
                "source": "checkWord",
                "dest": "tmpCheckWord", 
                # "conditions": "is_going_to_tmpCheckWord",
            },
            {
                "trigger": "go_back", 
                "source": ["checkWord","findWord", "tmpFindWord"],
                "dest": "dict",
            },
            {
                "trigger": "go_back_jisho", 
                "source": ["findTanngo"],
                "dest": "jisho",
            },
            {
                "trigger": "go_back_user", 
                "source": ["findWord", "findTanngo", "showFsm", "greet"],
                "dest": "user",
            },
            {
                "trigger": "advance", 
                "source": "intro",
                "dest": "user",
            },
            {
                "trigger": "advance", 
                "source": "findTanngo",
                "dest": "user",
                "conditions": "is_findTanngo_to_User"
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