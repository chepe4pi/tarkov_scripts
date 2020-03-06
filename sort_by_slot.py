import json
import os
import shutil

from selenium import webdriver

fp = webdriver.FirefoxProfile()
driver = webdriver.Firefox(firefox_profile=fp)


BOT_DIRS = os.path.join('db', 'bots')
SLOT_ID = 'FirstPrimaryWeapon'

tpl_to_object_file = open('tpl_to_object.json', 'r')
tpl_to_object = json.load(tpl_to_object_file)
tpl_to_object_file.close()

new_objects_paths_file = open('new_objects_paths_file.json', 'w')
new_objects_paths = {}

counter = 0
max_counter = 100000


class CounterException(Exception):
    pass


def parse_items(items, path, inventory, bot_name):
    global counter

    for item in items:
        if item and 'slotId' in item.keys() and item['slotId'] == SLOT_ID:
            tpl = item['_tpl']
            url = f'http://eft.maoci.eu/?q={tpl}'

            if tpl not in tpl_to_object.keys():
                driver.get(url)
                p_element = driver.find_element_by_class_name(name='ant-divider-inner-text')
                name = str(p_element.text).split(':')[1].strip().replace('/', '-').replace("\\", "-").replace('А', 'A')
                tpl_to_object[tpl] = name
            else:
                name = tpl_to_object[tpl]

            new_path = os.path.join(path, name)
            if not os.path.exists(new_path):
                os.mkdir(new_path)
            new_inventory_name = bot_name + "_" + inventory
            path_to_inventory = os.path.join(path, inventory)
            new_path_to_inventory = os.path.join(new_path, new_inventory_name)
            if not os.path.exists(new_path_to_inventory):
                shutil.copyfile(path_to_inventory, new_path_to_inventory)
                new_objects_paths[new_inventory_name] = new_path_to_inventory

            counter += 1

        if counter > max_counter:
            print('exit by counter')
            raise CounterException('exit by counter')


def create_tpl_to_obj_map():
    for bot_dir in os.listdir(BOT_DIRS):
        path = os.path.join(BOT_DIRS, bot_dir, 'inventory')
        for inventory in os.listdir(path):
            path_to_inventory = os.path.join(path, inventory)
            if os.path.isdir(path_to_inventory):
                continue
            inv_obj = json.load(open(path_to_inventory, 'r'))
            try:
                try:
                    items = inv_obj['items']
                    parse_items(items, path, inventory, bot_dir)
                except TypeError:
                    for items_all in inv_obj:
                        items = items_all['items']
                        parse_items(items, path, inventory, bot_dir)
            except CounterException:
                return


create_tpl_to_obj_map()
tpl_to_object_file = open('tpl_to_object.json', 'w')
tpl_to_object_file.write(json.dumps(tpl_to_object))
tpl_to_object_file.close()

new_objects_paths_file.write(json.dumps(new_objects_paths))
new_objects_paths_file.close()
