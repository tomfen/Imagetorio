function makePrinter(idx, width, direction, items) {

    blueprint = {
        "blueprint": {
            "entities": [],
            "icons": [],
            "item": "blueprint",
            "version": 73016672256
        }
    }

    idx = reshape(idx, width);

    var stripes = getStripes(idx, direction);

    counter = {
        i: -1,
        next: function () { return ++this.i },
        last: function () { return this.i },
    }

    var w = Math.floor(stripes.length/2)
    for (var x = 0; x < w; x++) {

        stripe = stripes[x]

        put_canvas(blueprint, counter, x, -1, Math.floor(stripe.length / 8))
        put_splitter(blueprint, counter, x, 0)
        var [divider, bit_shifter] =
            put_decoder(blueprint, counter, x, 7)
        put_memory(blueprint, counter, x, 31, divider, bit_shifter, stripe, items)
    }


    return exportBlueprint(blueprint)
}

function exportBlueprint(obj) {
    var string = JSON.stringify(obj)
    var binaryString = pako.deflate(string, { to: 'string' });
    var base64 = btoa(binaryString)
    return '0' + base64;
}

function getStripes(idx, direction) {
    var height = idx.length;
    var width = idx[0].length;

    stripes = []

    switch (direction) {
        case 'n':
            var reversed = getStripes(idx, 's').reverse()
            reversed.forEach(stripe => {
                stripes.push(stripe.reverse())
            });
            break;

        case 'w':
            for (var y = 0; y < height; y += 2) {
                var stripe = []

                for (var x = width - 1; x >= 0; x--) {
                    stripe.push(idx[y + 1][x])
                    stripe.push(idx[y][x])
                }

                stripes.push(stripe)
            }
            break;

        case 's':
            for (var x = 0; x < width; x += 2) {
                var stripe = []

                for (var y = 0; y < height; y++) {
                    stripe.push(idx[y][x + 1])
                    stripe.push(idx[y][x])
                }

                stripes.push(stripe)
            }
            break;

        case 'e':
            var reversed = getStripes(idx, 'w').reverse()
            reversed.forEach(stripe => {
                stripes.push(stripe.reverse())
            });
            break;
    }

    return stripes;
}

function reshape(arr, newWidth) {
    var newArr = [];
    while (arr.length) newArr.push(arr.splice(0, newWidth));

    return newArr;
}

var Direction = {
    N: 0,
    E: 2,
    S: 4,
    W: 6,
}

function put_canvas(blueprint, counter, x, y, length) {
    for (var i = 0; i < length; i++) {
        belt = { 'entity_number': counter.next(), 'name': 'express-transport-belt', 'position': { 'x': x, 'y': y - i } }
        blueprint['blueprint']['entities'].push(belt)
    }
}

function put_splitter(blueprint, counter, x, y) {

    const UNDR = 'express-underground-belt'
    const BELT = 'express-transport-belt'
    const SPLT = 'express-splitter'

    var entities
    if (x % 2 == 0) {
        entities = [
            { 'entity_number': counter.next(), 'name': UNDR, 'position': { 'x': x, 'y': y }, 'type': 'output' },
            { 'entity_number': counter.next(), 'name': BELT, 'position': { 'x': x - 1, 'y': y + 4 }, 'direction': Direction.E },
            { 'entity_number': counter.next(), 'name': UNDR, 'position': { 'x': x, 'y': y + 3 }, 'type': 'input' },
            { 'entity_number': counter.next(), 'name': BELT, 'position': { 'x': x, 'y': y + 4 } },
            { 'entity_number': counter.next(), 'name': BELT, 'position': { 'x': x, 'y': y + 6 } },
            { 'entity_number': counter.next(), 'name': SPLT, 'position': { 'x': x - .5, 'y': y + 5 } }]
    }
    else {
        entities = [
            { 'entity_number': counter.next(), 'name': BELT, 'position': { 'x': x, 'y': y } },
            { 'entity_number': counter.next(), 'name': SPLT, 'position': { 'x': x - .5, 'y': y + 2 } },
            { 'entity_number': counter.next(), 'name': BELT, 'position': { 'x': x - 1, 'y': y + 1 }, 'direction': Direction.E },
            { 'entity_number': counter.next(), 'name': BELT, 'position': { 'x': x, 'y': y + 1 } },
            { 'entity_number': counter.next(), 'name': UNDR, 'position': { 'x': x, 'y': y + 3 }, 'type': 'output' },
            { 'entity_number': counter.next(), 'name': UNDR, 'position': { 'x': x, 'y': y + 6 }, 'type': 'input' }]
    }

    entities.forEach(entity => {
        blueprint['blueprint']['entities'].push(entity)
    });
}

function connect(wire, first, second, first_circuit = 1, second_circuit = 1) {
    var ent2id = second['entity_number']

    if (!('connections' in first)) {
        first['connections'] = {}
    }

    if (!(first_circuit in first['connections'])) {
        first['connections'][first_circuit] = {}
    }

    if (!(wire in first['connections'][first_circuit])) {
        first['connections'][first_circuit][wire] = []
    }

    first['connections'][first_circuit][wire].push({ 'entity_id': ent2id, 'circuit_id': second_circuit })
}

function put_decoder(blueprint, counter, x, y) {
    blueprint['blueprint']['entities'].push({ 'entity_number': counter.next(), 'name': 'express-underground-belt', 'position': { 'x': x, 'y': y }, 'type': 'output' })
    blueprint['blueprint']['entities'].push({ 'entity_number': counter.next(), 'name': 'express-underground-belt', 'position': { 'x': x, 'y': y + 9 }, 'type': 'input' })

    requester = {
        'entity_number': counter.next(),
        'name': 'logistic-chest-requester',
        'position': { 'x': x, 'y': y + 11 },
        'control_behavior': { 'circuit_mode_of_operation': 1 }
    }

    multiplier = {
        'entity_number': counter.next(),
        'name': 'arithmetic-combinator',
        'position': { 'x': x, 'y': y + 5.5 },
        'direction': Direction.S,
        'control_behavior': {
            'arithmetic_conditions': {
                'first_signal': { 'type': 'virtual', 'name': 'signal-each' },
                'second_constant': 5,
                'operation': '*',
                'output_signal': { 'type': 'virtual', 'name': 'signal-each' }
            }
        }
    }

    inserter = {
        'entity_number': counter.next(),
        'name': 'stack-filter-inserter',
        'position': { 'x': x, 'y': y + 10 },
        'direction': Direction.S,
        'control_behavior': {
            'circuit_mode_of_operation': 1,
            'circuit_read_hand_contents': true
        },
        'override_stack_size': 1
    }

    pulse_conv = {
        'entity_number': counter.next(),
        'name': 'decider-combinator',
        'position': { 'x': x, 'y': y + 13.5 },
        'direction': Direction.S,
        'control_behavior': {
            'decider_conditions': {
                'first_signal': { 'type': 'virtual', 'name': 'signal-anything' },
                'constant': 0, 'comparator': '>',
                'output_signal': { 'type': 'virtual', 'name': 'signal-I' },
                'copy_count_from_input': false
            }
        }
    }

    bit_shifter = {
        'entity_number': counter.next(),
        'name': 'arithmetic-combinator',
        'position': { 'x': x, 'y': y + 19.5 },
        'control_behavior': {
            'arithmetic_conditions': {
                'first_signal': { 'type': 'virtual', 'name': 'signal-each' },
                'second_signal': { 'type': 'virtual', 'name': 'signal-I' },
                'operation': '>>',
                'output_signal': { 'type': 'virtual', 'name': 'signal-each' }
            }
        }
    }

    bit_and = {
        'entity_number': counter.next(),
        'name': 'arithmetic-combinator',
        'position': { 'x': x, 'y': y + 17.5 },
        'control_behavior': {
            'arithmetic_conditions': {
                'first_signal': { 'type': 'virtual', 'name': 'signal-each' },
                'second_constant': 1,
                'operation': 'AND',
                'output_signal': { 'type': 'virtual', 'name': 'signal-each' }
            }
        }
    }

    it_counter = {
        'entity_number': counter.next(),
        'name': 'arithmetic-combinator',
        'position': { 'x': x, 'y': y + 15.5 },
        'direction': Direction.S,
        'control_behavior': {
            'arithmetic_conditions': {
                'first_signal': { 'type': 'virtual', 'name': 'signal-I' },
                'second_constant': 1,
                'operation': '*',
                'output_signal': { 'type': 'virtual', 'name': 'signal-I' }
            }
        }
    }

    divider = {
        'entity_number': counter.next(),
        'name': 'arithmetic-combinator',
        'position': { 'x': x, 'y': y + 22.5 },
        'direction': Direction.S,
        'control_behavior': {
            'arithmetic_conditions': {
                'first_signal': { 'type': 'virtual', 'name': 'signal-I' },
                'second_constant': 32,
                'operation': '/',
                'output_signal': { 'type': 'virtual', 'name': 'signal-G' }
            }
        }
    }

    connect('green', multiplier, requester, first_circuit = 2)
    connect('green', inserter, multiplier, second_circuit = 1)
    connect('red', pulse_conv, inserter, first_circuit = 1)
    connect('red', bit_shifter, it_counter, first_circuit = 1, second_circuit = 2)
    connect('red', bit_shifter, divider, first_circuit = 1, second_circuit = 1)
    connect('green', bit_shifter, bit_and, first_circuit = 2, second_circuit = 1)
    connect('green', bit_and, inserter, first_circuit = 2)
    connect('green', it_counter, it_counter, first_circuit = 1, second_circuit = 2)
    connect('red', it_counter, pulse_conv, first_circuit = 1, second_circuit = 2)

    entities = [requester, multiplier, inserter, pulse_conv, bit_shifter, bit_and, it_counter, divider]

    entities.forEach(entity => {
        blueprint['blueprint']['entities'].push(entity)
    });

    if (x % 7 == 0) {
        [y + 7, y + 12, y + 21].forEach(_y => {
            pole = {
                "entity_number": counter.next(),
                "name": "medium-electric-pole",
                "position": { "x": x, "y": _y }
            }

            blueprint["blueprint"]["entities"].push(pole)
        })
    }


    if (x % 4 == 0) {
        roboport = {
            "entity_number": counter.next(),
            "name": "roboport",
            "position": { "x": x + 1.5, "y": y + 2.5 }
        }
        blueprint["blueprint"]["entities"].push(roboport)
    }

    return [divider, bit_shifter]
}

function bit_vector_to_int(arr) {
    var ret = 0

    for (var i = 0; i < arr.length; i++) {
        ret |= arr[i] << i
    }

    return ret
}

function put_memory(blueprint, counter, x, entity_y, divider, bit_shifter, id_list, names) {

    for (var i = 0; i < id_list.length; i += 32) {

        var strip = id_list.slice(i, i + 32)
        var strip_number = Math.floor(i / 32)

        var filters = []

        function onlyUnique(value, index, self) {
            return self.indexOf(value) === index;
        }

        var unique = strip.filter(onlyUnique);

        unique.forEach(item_idx => {
            var item = names[item_idx]

            var item_bit_vector = strip.map(v => { if (v == item_idx) return 1; else return 0 })

            var integer = bit_vector_to_int(item_bit_vector)

            filters.push({
                "count": integer,
                "index": filters.length % 18 + 1,
                "signal": { "type": "item", "name": item },
            })
        })

        var decider_connections
        if (strip_number == 0) {
            decider_connections = {
                "1": {
                    "red": [{
                        "entity_id": divider["entity_number"],
                        "circuit_id": 2
                    }]
                },
                "2": {
                    "green": [{
                        "entity_id": bit_shifter["entity_number"],
                        "circuit_id": 1
                    }]
                }
            }
        } else {
            decider_connections = {
                "1": {
                    "red": [{
                        "entity_id": decider_combinator["entity_number"],
                        "circuit_id": 1
                    }]
                },
                "2": {
                    "green": [{
                        "entity_id": decider_combinator["entity_number"],
                        "circuit_id": 2
                    }]
                }
            }
        }
        var decider_combinator = {
            "connections": decider_connections,
            "control_behavior": {
                "decider_conditions": {
                    "first_signal": { "type": "virtual", "name": "signal-G" },
                    "constant": strip_number,
                    "comparator": "=",
                    "output_signal": { "type": "virtual", "name": "signal-everything" },
                    "copy_count_from_input": "true"
                }
            },
            "direction": Direction.N,
            "entity_number": counter.next(),
            "name": "decider-combinator",
            "position": { "x": x, "y": entity_y + 0.5 }
        }

        var constant_combinator1 = {
            "connections": {
                "1": {
                    "green": [{
                        "entity_id": counter.last(),
                        "circuit_id": 1
                    }]
                }
            },
            "control_behavior": { "filters": filters.slice(0, 18) },
            "entity_number": counter.next(),
            "name": "constant-combinator",
            "position": { "x": x, "y": entity_y + 2 }
        }

        blueprint["blueprint"]["entities"].push(decider_combinator)
        blueprint["blueprint"]["entities"].push(constant_combinator1)

        if (filters.length > 18) {
            constant_combinator2 = {
                "connections": {
                    "1": {
                        "green": [{
                            "entity_id": counter.last(),
                            "circuit_id": 1,
                        }]
                    }
                },
                "control_behavior": { "filters": filters.slice(18) },
                "entity_number": counter.next(),
                "name": "constant-combinator",
                "position": { "x": x, "y": entity_y + 3 }
            }

            blueprint["blueprint"]["entities"].push(constant_combinator2)
        }


        if (x % 7 == 0) {
            pole = {
                "entity_number": counter.next(),
                "name": "medium-electric-pole",
                "position": { "x": x, "y": entity_y + 3 }
            }

            blueprint["blueprint"]["entities"].push(pole)
        }

        entity_y += 4
    }
}
