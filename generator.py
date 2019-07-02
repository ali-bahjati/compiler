import logging

logging.basicConfig(filename='generator.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
# logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('Generator')


def process_actions(action_list : list, curr_token):
    print(action_list, curr_token)
    return
