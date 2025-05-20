import argparse

def get_parser(desc: str):
    # define Arguemnts
    parser = argparse.ArgumentParser(desc)

    # Optional argument for selecting the UI
#    parser.add_argument(
#        '--ui', 
#        choices=['webUI', 'console'],  # Available options
#        default='webUI',  # Default value
#        type=str,  # Argument type
#        help="Select the UI: 'webUI' (default)."
    #)

    # Optional argument for selecting the config directory
    parser.add_argument(
        '--data', 
        type=str,  # Argument type
        help="Set the data directory"
    )

    # Optional argument for selecting the log directory
    parser.add_argument(
        '--log', 
        type=str,  # Argument type
        help="Set the log directory"
    )


    # Positional argument for selecting the UI (defaults to 'webUI')
    #parser.add_argument('ui_positional',
    #    nargs='?',  # Makes it optional
    #    choices=['webUI', 'console', 'none'],
    #    help="Select the UI (same as --ui option)."
    #)

    return parser
