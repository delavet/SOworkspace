import re
'''
处理code元素及概念名字的util类
'''


class CodeElementNameUtil:
    PATTERN_2_4 = re.compile(r'([A-Za-z])([24])([A-CE-Za-ce-z])')
    PATTERN_split = re.compile(r'([A-Z]+)([A-Z][a-z0-9]+)')
    PATTERN_split_num = re.compile(r'([0-9]?[A-Z]+)')

    def get_simple_name_with_parent(self, name):
        if not name:
            return None
        team_name = name.split("(")[0]
        split_names = team_name.split(".")
        if len(split_names) <= 1:
            return split_names[-1]

        child = split_names[-1].strip()
        parent = split_names[-2].strip()

        return parent + "." + child

    def simplify(self, name):
        """
        get the simple name for class, method, field, eg. java.util.ArrayList->ArrayList
        :param name:
        :return:
        """
        if not name:
            return None
        team_name = name.split("(")[0]
        simple_name = team_name.split(".")[-1].strip()

        return simple_name

    def uncamelize_from_simple_name(self, name):
        """
        uncamel from simple name of one name, rg. java.util.ArrayList->Array List
        :param name:
        :return:
        """
        if not name:
            return None
        simple_name = self.simplify(name)

        return self.uncamelize(simple_name)

    def uncamelize(self, name):
        """
        uncamel one name
        :param name: the camel styple name(include underline)
        :return:
        """
        if not name:
            return None
        # sub = re.sub(r'([A-Za-z])([24])([A-CE-Za-ce-z])', r'\1 \2 \3', name).strip()
        sub = re.sub(self.PATTERN_2_4, r'\1 \2 \3', name).strip()
        sub = re.sub(r'_', " ", sub)
        # sub = re.sub(r'([A-Z]+)([A-Z][a-z0-9]+)', r'\1 \2', sub)
        sub = re.sub(self.PATTERN_split, r'\1 \2', sub)
        # sub = re.sub(r'([0-9]?[A-Z]+)', r' \1', sub)
        sub = re.sub(self.PATTERN_split_num, r' \1', sub)
        sub = re.sub(r'\s+', " ", sub).strip()
        return sub

    def uncamelize_by_stemming(self, name):
        """
        uncamelzie the name and remove last num, eg. Student1->Student, JavaParser3->Java Parser
        :param name:
        :return:
        """
        # todo: improve this method to fix more situation, has some error for Path1->Path
        name = re.sub(r'([0-9]+)$', '', name)
        name = self.uncamelize(name)
        if not name:
            return None
        sub = self.match_numer_first_and_middle(name)
        if sub:
            return sub
        # self.merge_after_uncamelize_and_stemm(name)
        return name

    def match_numer_first_and_middle(self, name):
        number_first = re.compile(
            r'(^[0-9]+[A-Z]+)', re.IGNORECASE).findall(name)
        if number_first:
            return number_first[0]
        else:
            number_middle = re.compile(
                r'([A-Z]+[24][A-Z]+)', re.IGNORECASE).findall(name.replace(" ", ""))
            if number_middle:
                return number_middle[0]
            else:
                return None

    def generate_aliases(self, qualified_name, include_simple_parent_name=False):
        if not qualified_name:
            return []

        simple_name = self.simplify(qualified_name)
        separate_name = self.uncamelize_from_simple_name(simple_name)
        name_list = [simple_name, separate_name]

        if include_simple_parent_name:
            name_list.append(self.get_simple_name_with_parent(qualified_name))

        name_list = [name for name in name_list if name]

        return list(set(name_list))


class ConceptElementNameUtil:
    PATTERN_2_4 = re.compile(r'([A-Za-z])([24])([A-CE-Za-ce-z])')
    PATTERN_split = re.compile(r'([A-Z]+)([A-Z][a-z0-9]+)')
    PATTERN_split_num = re.compile(r'([0-9]?[A-Z]+)')

    def get_simple_name_with_parent(self, name):
        if not name:
            return None
        team_name = name.split("(")[0]
        split_names = team_name.split(".")
        if len(split_names) <= 1:
            return split_names[-1]

        child = split_names[-1].strip()
        parent = split_names[-2].strip()

        return parent + "." + child

    def simplify(self, name):
        """
        get the simple name for class, method, field, eg. java.util.ArrayList->ArrayList
        :param name:
        :return:
        """
        if not name:
            return None
        team_name = name.split("(")[0]
        simple_name = team_name.split(".")[-1].strip()

        return simple_name

    def uncamelize_from_simple_name(self, name):
        """
        uncamel from simple name of one name, rg. java.util.ArrayList->Array List
        :param name:
        :return:
        """
        if not name:
            return None
        simple_name = self.simplify(name)

        return self.uncamelize(simple_name)

    def uncamelize(self, name):
        """
        uncamel one name
        :param name: the camel styple name(include underline)
        :return:
        """
        if not name:
            return None
        # sub = re.sub(r'([A-Za-z])([24])([A-CE-Za-ce-z])', r'\1 \2 \3', name).strip()
        sub = re.sub(self.PATTERN_2_4, r'\1 \2 \3', name).strip()
        sub = re.sub(r'_', " ", sub)
        # sub = re.sub(r'([A-Z]+)([A-Z][a-z0-9]+)', r'\1 \2', sub)
        sub = re.sub(self.PATTERN_split, r'\1 \2', sub)
        # sub = re.sub(r'([0-9]?[A-Z]+)', r' \1', sub)
        sub = re.sub(self.PATTERN_split_num, r' \1', sub)
        sub = re.sub(r'\s+', " ", sub).strip()
        return sub

    def uncamelize_by_stemming(self, name):
        """
        uncamelzie the name and remove last num, eg. Student1->Student, JavaParser3->Java Parser
        :param name:
        :return:
        """
        # todo: improve this method to fix more situation, has some error for Path1->Path
        name = re.sub(r'([0-9]+)$', '', name)
        name = self.uncamelize(name)
        if not name:
            return None
        sub = self.match_numer_first_and_middle(name)
        if sub:
            return sub
        # self.merge_after_uncamelize_and_stemm(name)
        return name

    def match_numer_first_and_middle(self, name):
        number_first = re.compile(
            r'(^[0-9]+[A-Z]+)', re.IGNORECASE).findall(name)
        if number_first:
            return number_first[0]
        else:
            number_middle = re.compile(
                r'([A-Z]+[24][A-Z]+)', re.IGNORECASE).findall(name.replace(" ", ""))
            if number_middle:
                return number_middle[0]
            else:
                return None

    def generate_aliases(self, qualified_name, vocabulary=None, abbreviation=False):
        if not qualified_name:
            return []

        simple_name = self.simplify(qualified_name)
        of_names = self.deal_with_adj(simple_name)
        separate_name = self.uncamelize_from_simple_name(simple_name)
        name_deal_number = self.uncamelize_by_stemming(simple_name)
        combined_name = simple_name.lower().replace(
            "-", "").replace("\\", "").replace(" ", "")

        name_list = [simple_name, separate_name,
                     name_deal_number, combined_name]
        name_list.extend(of_names)

        if abbreviation:
            result = self.generate_all_abbreviation_names(
                separate_name, vocabulary)
            name_list.extend(result)

        name_list = [name for name in name_list if name]

        return list(set(name_list))

    def generate_all_abbreviation_names(self, separate_name, vocabulary):
        result = []
        part_abbreviation = []
        full_abbreviation_name = self.get_abbreviation(separate_name)
        abbreviation_name = self.get_abbreviation(
            separate_name, full_link=False)
        if vocabulary != None:
            part_abbreviation = self.get_part_abbreviation(
                separate_name, vocabulary)
        result.append(full_abbreviation_name)
        result.append(abbreviation_name)
        result.extend(part_abbreviation)

        return result

    def deal_with_adj(self, name):
        result = []
        seperate_words = [" of ", " Of "]

        # A of B type
        for s_w in seperate_words:
            if s_w in name:
                words = name.split(s_w)
                if len(words) != 2:
                    continue
                child = words[0]
                parent = words[1]
                result.append((parent + " " + child).replace("  ", " "))

        seperate_words = ["'s ", "' "]

        # A's B => A B
        for s_w in seperate_words:
            if s_w in name:
                words = name.split(s_w)
                if len(words) != 2:
                    continue
                parent = words[0]
                child = words[1]

                result.append((parent + " " + child).replace("  ", " "))
                result.append((child + " of " + parent).replace("  ", " "))

        return result

    def get_abbreviation(self, separate_name, full_link=True):
        separate_name_list = separate_name.lower().split(" ")
        if len(separate_name_list) <= 1:
            return separate_name
        if full_link:
            abbreviation_list = [name[0].upper()
                                 for name in separate_name_list]
            return "".join(abbreviation_list)
        else:
            abbreviation_list = [name[0].upper() for name in separate_name_list if
                                 name not in ["of", "the", "this", "a", "that"]]
            return "".join(abbreviation_list)

    def get_part_abbreviation(self, separate_name, vocabulary):
        """
        :param separate_name: term name
        :param vocabulary: a list of prase
        :return: a list of abbreviation
        """
        separate_name_list = separate_name.split(" ")
        return_list = []
        if len(separate_name_list) > 1:
            for index in range(len(separate_name_list) - 1):
                for inner_index in range(index + 1, len(separate_name_list)):
                    prase = " ".join(separate_name_list[index:inner_index + 1])
                    if prase in vocabulary:
                        abbreviation_list = [
                            name[0].upper() for name in separate_name_list[index:inner_index + 1]]
                        abbreviation = separate_name.replace(
                            prase, "".join(abbreviation_list))
                        return_list.append(abbreviation)
            return return_list
        else:
            return [separate_name]
