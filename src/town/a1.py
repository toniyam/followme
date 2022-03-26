from char import IChar
from item.item_finder import ItemFinder
from logger import Logger
from town.i_act import IAct
from screen import convert_monitor_to_screen, convert_screen_to_abs, grab
from config import Config
from npc_manager import Npc, open_npc_menu, press_npc_btn
from pather import Pather, Location
from typing import Union
from template_finder import TemplateFinder
from ui_manager import ScreenObjects, is_visible
from utils.misc import wait
from screen import convert_abs_to_monitor
from utils.custom_mouse import mouse

class A1(IAct):
    def __init__(self, pather: Pather, char: IChar):
        self._pather = pather
        self._char = char

    def get_wp_location(self) -> Location: return Location.A1_WP_NORTH
    def can_resurrect(self) -> bool: return True
    def can_buy_pots(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_heal(self) -> bool: return True
    def can_stash(self) -> bool: return True
    def can_trade_and_repair(self) -> bool: return True

    def resurrect(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_KASHYA_CAIN), self._char, force_move=True):
            return False
        if open_npc_menu(Npc.KASHYA):
            press_npc_btn(Npc.KASHYA, "resurrect")
            return Location.A1_KASHYA_CAIN
        return False

    def open_wp(self, curr_loc: Location) -> bool:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_WP_SOUTH), self._char, force_move=True): return False
        wait(0.5, 0.7)
        if not TemplateFinder().search("A1_WP", grab()).valid:
            curr_loc = Location.A1_WP_SOUTH
            if not self._pather.traverse_nodes((curr_loc, Location.A1_WP_NORTH), self._char, force_move=True): return False
            wait(0.5, 0.7)
        found_wp_func = lambda: is_visible(ScreenObjects.WaypointLabel)
        # decreased threshold because we sometimes walk "over" it during pathing
        return self._char.select_by_template(["A1_WP"], found_wp_func, threshold=0.62)

    def wait_for_tp(self) -> Union[Location, bool]:
        success = TemplateFinder().search_and_wait(["A1_TOWN_7", "A1_TOWN_9"], timeout=20).valid
        if not self._pather.traverse_nodes([Location.A1_TOWN_TP, Location.A1_KASHYA_CAIN], self._char, force_move=True): return False
        if success:
            return Location.A1_KASHYA_CAIN
        return False

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_KASHYA_CAIN), self._char, force_move=True): return False
        if open_npc_menu(Npc.CAIN):
            press_npc_btn(Npc.CAIN, "identify")
            return Location.A1_KASHYA_CAIN
        return False

    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]:
        Logger.debug('30 countdown')
        wait(33.5, 33.7)
        while True:
            found = TemplateFinder().search("A1_CEO", grab())
            if found.valid:
                Logger.debug(' center value')
                Logger.debug(found.center)
                # x_coor = found.center[0] - 640
                # y_coor = found.center[1] - 360
                # Logger.debug(x_coor)
                # Logger.debug(y_coor)
                #  x_m, y_m = convert_abs_to_monitor([x_coor, y_coor])
                x_m, y_m = convert_abs_to_monitor(found.center)
                Logger.debug('moving mon value')
                Logger.debug(x_m)
                Logger.debug(y_m)
                # self._char.move((x_m - 1000, y_m - 1000), force_move=True)
                # self._char.move((found.center[0], found.center[1]), force_move=True)
                factor = Config().advanced_options["pathing_delay_factor"]
                pos_screen = convert_monitor_to_screen(found.center)
                pos_abs = convert_screen_to_abs(pos_screen)
                x_m, y_m = convert_abs_to_monitor(pos_abs)
                mouse.move(x_m, y_m + 40, randomize=5, delay_factor=[factor*0.1, factor*0.14])
                mouse.click(button="left")
                wait(0.5, 1.2)
            else:
                wait(1.5, 1.7)
        # x_m, y_m = convert_abs_to_monitor([110, 122])
        # self._char.move((x_m, y_m), force_move=True)
        # if not self._pather.traverse_nodes([228], self._char, force_move=True): return False
        # open_npc_menu(Npc.AKARA)
        # press_npc_btn(Npc.AKARA, "trade")
        return Location.A1_AKARA

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_STASH), self._char, force_move=True):
            return False
        wait(0.5, 0.6)
        def stash_is_open_func():
            img = grab()
            found = is_visible(ScreenObjects.GoldBtnInventory, img)
            found |= is_visible(ScreenObjects.GoldBtnStash, img)
            return found
        if not self._char.select_by_template(["A1_TOWN_0"], stash_is_open_func):
            return False
        return Location.A1_STASH

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_AKARA), self._char, force_move=True): return False
        open_npc_menu(Npc.AKARA)
        return Location.A1_AKARA

    def open_trade_and_repair_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_CHARSI), self._char, force_move=True): return False
        open_npc_menu(Npc.CHARSI)
        press_npc_btn(Npc.CHARSI, "trade_repair")
        return Location.A1_CHARSI
