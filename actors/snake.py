import collections

import math

from SnakeGame.constants.direction import Direction


class Segment:
    SEGMENT_LENGTH = 20
    SEGMENT_WIDTH = 20
    HEAD = 'head'
    TAIL = 'tail'
    BODY = 'body'
    ANGLE_VARIATION = 20
    CONST = math.degrees(math.atan(0.5))

    def __init__(self, board, direction, x, y, type, tail_angle=0):
        self.board = board
        self.index = None

        self.x, self.y = x, y
        self.coords = ()
        self.direction = direction
        self.type = type
        self.tail_angle = tail_angle
        self.tail_direction = Direction.UP

    def get_rectangle_coords(self):
        x_coord, y_coord = self.x, self.y
        len_diff = Segment.SEGMENT_LENGTH / 2
        width_diff = Segment.SEGMENT_WIDTH / 2

        if self.direction in [Direction.LEFT, Direction.RIGHT]:
            rectangle_coords = x_coord - len_diff, y_coord - width_diff, x_coord + len_diff, y_coord + width_diff
        else:
            rectangle_coords = x_coord - width_diff, y_coord - len_diff, x_coord + width_diff, y_coord + len_diff

        return rectangle_coords

    def create(self):

        rectangle_coords = self.get_rectangle_coords()
        self.coords = rectangle_coords
        if self.type == Segment.HEAD:
            if self.direction == Direction.RIGHT:
                head_coords = rectangle_coords[0] - 2 * Segment.SEGMENT_WIDTH, rectangle_coords[1], rectangle_coords[
                    2] + Segment.SEGMENT_WIDTH, rectangle_coords[3]
                start, extent = -90, 180
            elif self.direction == Direction.LEFT:
                head_coords = rectangle_coords[0], rectangle_coords[1], rectangle_coords[2] + Segment.SEGMENT_WIDTH, \
                              rectangle_coords[3]
                start, extent = 90, 180
            elif self.direction == Direction.UP:
                head_coords = rectangle_coords[0], rectangle_coords[1], rectangle_coords[2], rectangle_coords[
                    3] + Segment.SEGMENT_LENGTH
                start, extent = 0, 180

            else:
                head_coords = rectangle_coords[0], rectangle_coords[1] - Segment.SEGMENT_LENGTH, rectangle_coords[2], \
                              rectangle_coords[3]
                start, extent = 0, -180

            index = self.board.create_rectangle(rectangle_coords, fill='green', tags=('head',))
        elif self.type == Segment.BODY:
            index = self.board.create_rectangle(rectangle_coords, fill='pink', tags=('body'))
        else:
            index = self.create_tail()

        self.index = index

    def create_tail(self):
        tail_angle = self.tail_angle

        if self.direction == Direction.RIGHT:
            self.coords = self.coords[0] - Segment.SEGMENT_WIDTH, self.coords[1], self.coords[2], self.coords[3]
            y1 = self.coords[1] + (self.coords[3] - self.coords[1]) / 2 + math.tan(math.radians(self.tail_angle)) * (
                    self.coords[2] - self.coords[0])
            index = self.board.create_polygon(self.coords[2], self.coords[3], self.coords[2], self.coords[1],
                                              self.coords[0], y1, fill='green')
        elif self.direction == Direction.LEFT:
            self.coords = self.coords[0], self.coords[1], self.coords[2] + Segment.SEGMENT_WIDTH, self.coords[3]
            y1 = self.coords[1] + (self.coords[3] - self.coords[1]) / 2 + math.tan(math.radians(self.tail_angle)) * (
                    self.coords[2] - self.coords[0])
            index = self.board.create_polygon(self.coords[0], self.coords[1], self.coords[0], self.coords[3],
                                              self.coords[2], y1,
                                              fill='green')
        elif self.direction == Direction.UP:
            self.coords = self.coords[0], self.coords[1], self.coords[2], self.coords[3] + Segment.SEGMENT_WIDTH
            x = self.coords[0] + (self.coords[2] - self.coords[0]) / 2 + math.tan(math.radians(self.tail_angle)) * (
                    self.coords[3] - self.coords[1])
            index = self.board.create_polygon(self.coords[0], self.coords[1], self.coords[2], self.coords[1], x,
                                              self.coords[3],
                                              fill='green')

        else:
            self.coords = self.coords[0], self.coords[1] - Segment.SEGMENT_WIDTH, self.coords[2], self.coords[3]
            x = self.coords[0] + (self.coords[2] - self.coords[0]) / 2 + math.tan(math.radians(self.tail_angle)) * (
                    self.coords[3] - self.coords[1])
            index = self.board.create_polygon(self.coords[0], self.coords[3], self.coords[2], self.coords[3], x,
                                              self.coords[1],
                                              fill='green')

        return index

    def change_direction(self, direction):
        self.direction = direction

    def configure(self, **kwargs):
        self.board.itemconfigure(self.index, **kwargs)

    def recreate(self, type, tail_angle=0, tail_direction=Direction.UP):
        self.board.delete(self.index)

        self.type = type

        if self.type == Segment.HEAD:
            index = self.board.create_rectangle(self.coords, fill='red', tags=('head'))
        elif self.type == Segment.BODY:
            index = self.board.create_rectangle(self.coords, fill='pink', tags=('body'))
        else:
            self.tail_direction = tail_direction
            if tail_direction == Direction.UP:
                self.tail_angle = tail_angle + Segment.ANGLE_VARIATION
                if self.tail_angle > Segment.CONST:
                    self.tail_direction = Direction.DOWN
                    self.tail_angle = Segment.CONST
            elif tail_direction == Direction.DOWN:
                self.tail_angle = tail_angle - Segment.ANGLE_VARIATION
                if self.tail_angle < -Segment.CONST:
                    self.tail_direction = Direction.UP
                    self.tail_angle = -Segment.CONST
            index = self.create_tail()
        self.index = index

    def get_pickleble_data(self):
        data = dict()
        data['x'] = self.x
        data['y'] = self.y
        data['direction'] = self.direction
        data['type'] = self.type
        data['tail_angle'] = self.tail_angle
        data['tail_direction'] = self.tail_direction

        return data


class Snake:

    def __init__(self, canvas):
        self.canvas = canvas
        self.segments = collections.deque([])
        self.speed = 100
        self.head = None
        self.tail = None

    def __str__(self):
        str_return = ''
        for segment in self.segments:
            str_return += "{}[{}]:[{}]->".format(segment.type, segment.index, [segment.x, segment.y])

        return str_return

    def increment_speed(self, increment_by):
        self.speed -= increment_by
        print("Speed incremented: {}".format(self.speed))

    def set_property(self, segments, **kwargs):
        for segment in segments:
            segment.configure(**kwargs)

    def add_segment(self, segment_type, direction, **kwargs):

        dx = dy = 0

        is_head = True if segment_type == Segment.HEAD else False
        is_body = True if segment_type == Segment.BODY else False
        is_tail = True if segment_type == Segment.TAIL else False

        if direction == Direction.UP:
            if is_head:
                dy = - Segment.SEGMENT_LENGTH
            else:
                dy = Segment.SEGMENT_LENGTH
        if direction == Direction.DOWN:
            if is_head:
                dy = Segment.SEGMENT_LENGTH
            else:
                dy = - Segment.SEGMENT_LENGTH
        if direction == Direction.LEFT:
            if is_head:
                dx = -Segment.SEGMENT_LENGTH
            else:
                dx = Segment.SEGMENT_LENGTH
        if direction == Direction.RIGHT:
            if is_head:
                dx = Segment.SEGMENT_LENGTH
            else:
                dx = - Segment.SEGMENT_LENGTH

        prev_head = None

        if is_head:
            if not len(self.segments):
                head_coords = kwargs['snake_init_coords']
            else:
                head = self.head
                head_coords = head.x, head.y
                prev_head = head

            x_coord_of_new_segment, y_coord_of_new_segment = head_coords[0] + dx, head_coords[1] + dy

            if x_coord_of_new_segment <= 0:
                x_coord_of_new_segment = self.canvas.width - Segment.SEGMENT_WIDTH
            if x_coord_of_new_segment >= self.canvas.width:
                x_coord_of_new_segment = Segment.SEGMENT_WIDTH
            if y_coord_of_new_segment <= 0:
                y_coord_of_new_segment = self.canvas.height - Segment.SEGMENT_WIDTH
            if y_coord_of_new_segment >= self.canvas.height:
                y_coord_of_new_segment = Segment.SEGMENT_WIDTH

        else:
            tail_coords = (self.tail.x, self.tail.y) if not kwargs else kwargs['snake_init_coords']

            x_coord_of_new_segment, y_coord_of_new_segment = tail_coords[0] + dx, tail_coords[1] + dy

        tail_angle = 0

        new_segment = Segment(self.canvas, direction, x_coord_of_new_segment,
                              y_coord_of_new_segment, segment_type, tail_angle)
        new_segment.create()

        if is_head:
            self.segments.append(new_segment)
            self.head = new_segment
            if not prev_head:
                self.tail = new_segment
            else:
                prev_head.recreate(Segment.BODY)
        elif is_tail:
            prev_tail = self.tail
            self.tail = new_segment
            self.segments.appendleft(new_segment)

            prev_tail.recreate(Segment.BODY)
        else:
            self.segments.appendleft(new_segment)
            self.tail = new_segment
        self.canvas.update()

    def remove_tail(self):
        segment = self.segments.popleft()
        tail_angle = segment.tail_angle
        tail_direction = segment.tail_direction
        self.canvas.delete(segment.index)

        del segment

        self.tail = self.segments[0]

        self.tail.recreate(Segment.TAIL, tail_angle, tail_direction)

    def get_pickleble_data(self):
        data = dict()
        data['segments'] = [segment.get_pickleble_data() for segment in self.segments]
        data['speed'] = self.speed
        data['head'] = self.head.get_pickleble_data()
        data['tail'] = self.tail.get_pickleble_data()

        return data

    @staticmethod
    def reconstruct(board, snake_data):
        speed = snake_data['speed']
        snake = Snake(board)
        snake.speed = speed

        segments_data = snake_data['segments']
        for segment_data in segments_data:
            segment_type = segment_data['type']
            direction = segment_data['direction']
            x = segment_data['x']
            y = segment_data['y']
            tail_angle = segment_data['tail_angle']
            tail_direction = segment_data['tail_direction']
            segment_obj = Segment(board, direction, x, y, segment_type, tail_angle)
            segment_obj.create()

            snake.segments.append(segment_obj)

            if segment_type == Segment.HEAD:
                snake.head = segment_obj
            if segments_data == Segment.TAIL:
                snake.tail = segment_obj
        return snake
