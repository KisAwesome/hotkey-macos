
class CodeError(Exception):
    pass

class ArgumentError(CodeError):
    pass

class FunctionNonExistant(CodeError):
    pass

class MissingBindingError(CodeError):
    pass



__buttons__ = ['left', 'right']

__all__ = ['bind', 'delay', 'cmd', 'click', 'typewrite',
           'website', 'press', 'open', 'move_mouse', 'loop', 'endloop', 'mode', 'clipboard','debug']

__modes__ = ['single', 'toggle', 'while_held']

__no_loop__ = ['bind', 'mode']

__vars__ = ['time','date','full_date']

function_argument_rules = {
    'bind': 1,
    'delay': 1,
    'cmd': 'all',
    'click': 1,
    'typewrite': 'all',
    'website': 'all',
    'press': 1,
    'open': 'all',
    'move_mouse': 2,
    'loop': 1,
    'mode': 1,
    'endloop': 0,
    'clipboard': 'all',
    'debug':'all'

}   

function_argument_type_rules = {
    'bind': str,
    'delay': float,
    'cmd': str,
    'click': str,
    'typewrite': str,
    'website': str,
    'press': str,
    'open': str,
    'move_mouse': str,
    'loop': int,
    'mode': str,
    'endloop': str,
    'clipboard': str,
    'debug':str

}


function_to_actions = {
    'delay': 'DELAY',
    'cmd':  'RUN_COMMAND',
    'click': 'CLICK_MOUSE',
    'typewrite':  'TYPEWRITE',
    'website': 'OPEN_WEBSITE',
    'press': 'PRESS_KEY',
    'open': 'LAUNCH_APP',
    'move_mouse': 'MOVE_MOUSE',
    'loop': 'LOOP',
    'clipboard': 'CLIPBOARD',
    'debug':'DEBUG'

}

actions = {
    'OPEN_WEBSITE': {'arg': 'url'},
    'DELAY': {'arg': 'duration'},
    'RUN_COMMAND': {'arg': 'command'},
    'PRESS_KEY': {'arg': 'key'},
    'TYPEWRITE': {'arg': 'text'},
    'CLICK_MOUSE': {'arg': 'button'},
    'MOVE_MOUSE': {'arg': 'pos'},
    'LAUNCH_APP': {'arg': 'path'},
    'LOOP': {'arg': 'x'},
    'CLIPBOARD': {'arg': 'text'},
    'DEBUG':{'arg':'message'}


}


def compile_source(path):
    FUNCTIONS = []
    BIND = None
    MODE = 'single'
    JSON_SCRIPT = {
        'src': []
    }
    with open(path) as file:
        scriptlines_raw = file.readlines()
        script_raw = file.read()

    scriptlines = []
    for i in scriptlines_raw:
        if i == '' or i == ' ' or i == '\n':
            continue
        scriptlines.append(i.replace('\n', ''))

    iter_line = 0
    for i in scriptlines:
        if i.startswith('#') or i.startswith('//'):
            continue
        iter_line += 1
        if i == '' or i == ' ' or i == '\n':
            continue
        hold = ''
        command = i.split(' ')[0]
        if not command in __all__:
            raise FunctionNonExistant(
                f'Line {iter_line}: Function does not exist {command}')

        line_ = i.split(' ')
        line = []
        for i in line_:
            if i == '' or i == ' ':
                continue
            line.append(i)

        command = line[0]
        FUNCTIONS.append(command)
        rule = function_argument_rules[command]
        if rule == 'all':
            if not len(line) >= 2:
                raise ArgumentError(
                    f'Line {iter_line}: {command} expected at least 1 argument,0 were given')
            continue

        if len(line) != rule + 1:
            raise ArgumentError(
                f'Line {iter_line}: {command} expected {rule} arguments, {len(line)-1} were given')

        ARG_TYPE = function_argument_type_rules[command]
        if ARG_TYPE != str:
            args = line[:]
            args.pop(0)

            for i in args:
                try:
                    ARG_TYPE(i)
                except:
                    raise TypeError(f'Line {iter_line}:Expected int not str')

    if not 'bind' in FUNCTIONS:
        raise MissingBindingError('Missing Keybind for script')

    index = 0
    excluded_items = []
    for i in scriptlines:
        if i.startswith('#') or i.startswith('//'):
            continue
        index += 1
        if index in excluded_items:
            print(index)
            continue
        line_ = i.split(' ')
        line = []
        for i in line_:
            if i == '' or i == ' ':
                continue
            line.append(i)
        command = line[0]
        rule = function_argument_rules[command]
        if rule != 0:
            ARGUMENT = line[1]

        if command == 'move_mouse':
            ARGUMENT = [int(line[1]), int(line[2])]

        if function_argument_type_rules[command] != str:
            Type = function_argument_type_rules[command]
            ARGUMENT = Type(ARGUMENT)

        if command == 'click':
            if not ARGUMENT in __buttons__:
                raise ArgumentError(f'Line {index+1}: invalid mouse button')

        # if command == 'loop':
        #     ITERATIONS = ARGUMENT
        #     inside_loop = scriptlines[index:]
        #     print(inside_loop)

        #     for nal in __no_loop__:
        #         if nal in inside_loop:
        #             raise NotExpected(
        #                 f'Line {index+1}:Unexpeted fucntion in loop {nal}')

        if function_argument_rules[command] == 'all':
            args = line[:]
            args.pop(0)
            ARGUMENT = ' '.join(args)

        if command == 'bind':
            BIND = ARGUMENT
            continue
        if command == 'mode':
            if not ARGUMENT in __modes__:
                raise ArgumentError(f'Line {index+1}: Invalid Mode')
            MODE = ARGUMENT
            continue

        JSON_SCRIPT['src'].append(
            {'cmd': function_to_actions[command], actions[function_to_actions[command]]['arg']: ARGUMENT})

    JSON_SCRIPT['key'] = BIND
    JSON_SCRIPT['run_mode'] = MODE
    return JSON_SCRIPT

