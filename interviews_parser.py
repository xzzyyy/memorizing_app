import os
import html.parser
import abc
import sys


class Parser(html.parser.HTMLParser, abc.ABC):
    NONE = 0
    QUESTION_ID = 1
    QUESTION = 2
    ANSWER = 3

    def __init__(self):
        super().__init__()
        self.tr_level = 0
        self.style_tag = False
        self.question_style = None
        self.state = self.NONE
        self.style = ''
        self.q_id = self.q = self.a = ""
        self.d = []
        self.content = ''

    def process_file(self, file_path, output_folder):
        def create_html(content):
            return '<html><head>' + self.style + '<body>' + content + '</body></head></html>'

        if not os.path.isdir(output_folder):
            print('no output folder:', output_folder)
            return 1
        for fn in os.listdir(output_folder):
            os.remove(output_folder + '/' + fn)

        f = open(file_path, 'rt')
        self.feed('\n'.join(f.readlines()))

        os.rmdir(output_folder)
        os.mkdir(output_folder)

        for tup in self.d:
            f_q = open(output_folder + '/' + tup['q_id'] + '.html', 'wt', encoding='utf-8-sig')
            f_q.write(create_html(tup['q']))
            f_q.close()

            f_a = open(output_folder + '/' + tup['q_id'] + '_a.html', 'wt', encoding='utf-8-sig')
            f_a.write(create_html(tup['a']))
            f_a.close()

        return 0

    def handle_starttag(self, tag, attrs):
        def unparse(t, ats):
            attrs_str = ' '.join([a[0] + '="' + a[1] + '"' for a in ats])
            return '<' + t + (' ' + attrs_str if len(attrs_str) > 0 else '') + '>'

        if tag == 'tr':
            self.tr_level += 1

        if tag == 'style':
            self.style_tag = True
            self.style += unparse(tag, attrs)

        elif tag == 'td' and self.tr_level == 1:
            if self.state == self.NONE:
                for attr_pair in attrs:
                    if attr_pair[0] == 'class':
                        styles = attr_pair[1].split(' ')
                        if self.question_style in styles:
                            self.state = self.QUESTION_ID

        elif (self.state == self.QUESTION_ID or self.state == self.QUESTION or self.state == self.ANSWER) \
                and self.tr_level >= 1 and tag != "tr":
            self.content += unparse(tag, attrs)

    def handle_data(self, data):
        if self.style_tag:
            self.style += data + '</style>'

            table_td = 'table td'
            idx_table_td = data.find(table_td)
            data = data[idx_table_td + len(table_td):]

            idx_cell_color = data.find('{background-color:#efefef}')
            idx_style_name = data.rfind('.', 0, idx_cell_color)
            self.question_style = data[idx_style_name + 1:idx_cell_color]
            print('cell color style:', self.question_style)

            self.style_tag = False

        elif self.state == self.QUESTION_ID and self.tr_level == 1:
            self.content += data

        elif self.state == self.QUESTION and self.tr_level >= 1:
            self.content += data

        elif self.state == self.ANSWER and self.tr_level >= 1:
            self.content += data

    def handle_endtag(self, tag):
        if tag == "tr":
            self.tr_level -= 1

        elif tag == "td" and self.tr_level == 1 and self.state == self.QUESTION_ID:
            self.q_id = self.remove_tags(self.content)
            self.content = ''
            self.state = self.QUESTION

        elif tag == "td" and self.tr_level == 1 and self.state == self.QUESTION:
            self.q = self.content
            self.content = ''
            self.state = self.ANSWER

        elif tag == "td" and self.tr_level == 1 and self.state == self.ANSWER:
            self.a = self.content
            self.content = ''
            self.d.append({'q_id': self.q_id, 'q': self.q, 'a': self.a})
            self.state = self.NONE

        elif (self.state == self.QUESTION or self.state == self.ANSWER) \
                and self.tr_level >= 1:
            self.content += '</' + tag + '>'

    @staticmethod
    def remove_tags(s):
        idx = s.find('<')
        while idx != -1:
            idx2 = s.find('>')
            s = s[0:idx] + s[idx2 + 1:]
            idx = s.find('<')
        return s


if __name__ == '__main__':
    p = Parser()
    p.process_file(sys.argv[1], sys.argv[2])
