import tcod
class Message:
    def __init__(self, text, color=tcod.white):
        self.text = text
        self.color = color

    def __repr__(self):
        return self.text

def message(*args, **kwargs):
    '''
    An implementation of message passing that is intended to be as flexible 
    as possible. It supports arguments dynamically by returning the kwargs as
    a dictionary.

    kwargs -> A n-amount of user supplied keyword arguments used by the
              message parser defined in game_messages.py.

                message - > A message keyword can be supplied to this function
                            to indicate plaintext to display to the console.
                            As such, the value of message is expected to be a
                            string, and this function will convert it into a 
                            Message() object.
    '''
    msg = kwargs.pop('message', None)
    if msg is not None:
        msg_color = kwargs.pop('color', tcod.white)
        msg = Message(msg, msg_color)
        kwargs['message'] = msg

    return kwargs