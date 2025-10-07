#!/usr/bin/env python3

import curses as c
import curses.textpad as ct
import os
import json

# This program is never-nesters' nightmare and i'm fully aware of if ~Onko o3o

"""
TODO
Add Shapeless crafting too (menu)
Add Smelting and shit

IN PROGRESS

DONE
Add legend to see keys
Add field editing
Add result block too
Add result saving to a file
Add "generate datapack" option too!

DONE 2
Add working with minecraft:air -> add space in pattern & <empty> -> no space adding in pattern

FUTURE
Make colored text generator
Make /give generator

"""

class Visuals:

	@staticmethod
	def inputBox(
		start_x: int,
		start_y: int,
		title: str,
		current_value: str,
		input_length: int = 75
	) -> str | None:
		width: int = max(len(title), input_length) + 8
		popup = c.newwin(8, width, start_y, start_x)

		selected_option: int = 0
		new_value: str = current_value
		popup.keypad(True)

		while True:
			popup.clear()
			popup.box()
			popup.addstr(1, 2, title, c.color_pair(3))

			textbox = popup.derwin(1, input_length, 3, 2)
			textbox.clear()

			if selected_option == 0:
				textbox.bkgd(' ', c.color_pair(2))
			else:
				textbox.bkgd(' ', c.color_pair(1))

			textbox.addstr(0, 0, new_value)
			textbox.attron(c.A_NORMAL)
			textbox.refresh()
			popup.refresh()

			popup.addstr(5, 2, "[Save]", c.A_REVERSE if selected_option == 1 else c.A_NORMAL)
			popup.addstr(6, 2, "[Exit]", c.A_REVERSE if selected_option == 2 else c.A_NORMAL)
			popup.refresh()

			key = popup.getch()

			if selected_option == 0:
				if key in (c.KEY_ENTER, 10, 13):
					textbox.bkgd(' ', c.color_pair(2))
					textbox.refresh()
					textboxObject: ct.Textbox = ct.Textbox(textbox)
					c.curs_set(1)
					entered_text: str = textboxObject.edit().strip()
					c.curs_set(0)
					new_value = entered_text
					selected_option = 1
				elif key == c.KEY_UP:
					selected_option = (selected_option -1) %3
				elif key == c.KEY_DOWN:
					selected_option = (selected_option +1) %3
			else:
				if key == c.KEY_UP:
					selected_option = (selected_option -1) %3
				elif key == c.KEY_DOWN:
					selected_option = (selected_option +1) %3
				elif key in (c.KEY_ENTER, 10, 13):
					textbox.clear()
					textbox.refresh()
					popup.clear()
					popup.box()
					popup.refresh()
					return new_value if selected_option == 1 else None

	@staticmethod
	def optionBox(
		start_x: int,
		start_y: int,
		title: str,
		*options: list[str]
	) -> str | None:
		height: int = len(options) + 5
		width: int = max(len(title), *(len(opt) for opt in options)) + 8

		popup = c.newwin(height, width, start_y, start_x)
		popup.keypad(True)
		selected_option: int = 0

		while True:
			popup.box()
			popup.refresh()
			popup.addstr(1, 2, title, c.color_pair(3))
			
			for index, option in enumerate(options):
				position: int = index +3
				if index == selected_option:
					popup.addstr(position, 2, option, c.color_pair(2))
				else:
					popup.addstr(position, 2, option, c.color_pair(1))

			key = popup.getch()

			if key == c.KEY_UP:
				selected_option = (selected_option -1) % len(options)
			elif key == c.KEY_DOWN:
				selected_option = (selected_option +1) % len(options)
			elif key == 27:
				popup.clear()
				popup.refresh()
				return None

			elif key in (c.KEY_ENTER, 10, 13):
				return options[selected_option]

	@staticmethod
	def drawHelpBar(stdscr) -> None:
		try:
			stdscr.attron(c.A_REVERSE)
			stdscr.addstr (
				c.LINES -2, 0,
				"[arrows] Navigate   [enter] Select   [tab] Go to result".ljust(c.COLS)
			)
			stdscr.attroff(c.A_REVERSE)
		except: pass

	@staticmethod
	def drawItemFrame (
		pos_x: int, pos_y: int,
		selected: bool,
		key_name: str = ""
	) -> None:
		item_frame = c.newwin(3, 5, pos_y, pos_x)
		item_frame.box()
		item_frame.addstr (
			1, 2,
			key_name if key_name else ' ',
			c.A_REVERSE if selected else c.A_NORMAL
		)
		item_frame.refresh()

	@staticmethod
	def drawLegend(keys: list) -> None:
		legend = c.newwin(len(keys) +3, 50, 15, 2)
		legend.addstr(1, 1, "Legend", c.color_pair(3))
		
		position: int = 0
		for key in keys:
			legend.addstr(position +2, 2, key["key_name"])
			legend.addstr(position +2, len(key["key_name"]) +2, f" - {key['item_id']}")
			position += 1

		legend.box()
		legend.refresh()

def craftingShaped (
	stdscr,
	start_x: int, start_y: int
) -> None:
	craftingData: dict = {
		"category": "",
		"keys": [
			# {"key_name": "X", "item_id": "minecraft:x"},
			# {"key_name": "Y", "item_id": "minecraft:y"},
			# {"key_name": "Z", "item_id": "minecraft:z"},
			# {"key_name": "A", "item_id": "minecraft:a"},
			# {"key_name": "B", "item_id": "minecraft:b"},
			# {"key_name": "C", "item_id": "minecraft:c"}
		],
		"pattern": [
			["", "", ""],
			["", "", ""],
			["", "", ""]
		],
		"result": {
			"item_id": "",
			"count": 1
		}
	}

	in_grid: bool = True
	sel_x, sel_y = 0, 0
	while True:
		stdscr.clear()
		stdscr.keypad(True)
		stdscr.addstr(0, 0, "Crafting", c.color_pair(3))

		Visuals.drawHelpBar(stdscr)
		stdscr.refresh()

		def itemFrameGenerator() -> None:
			Visuals.drawItemFrame(1, 2, sel_x == 0 and sel_y == 0 and in_grid, craftingData["pattern"][0][0])
			Visuals.drawItemFrame(6, 2, sel_x == 1 and sel_y == 0 and in_grid, craftingData["pattern"][0][1])
			Visuals.drawItemFrame(11, 2, sel_x == 2 and sel_y == 0 and in_grid, craftingData["pattern"][0][2])
			Visuals.drawItemFrame(1, 5, sel_x == 0 and sel_y == 1 and in_grid, craftingData["pattern"][1][0])
			Visuals.drawItemFrame(6, 5, sel_x == 1 and sel_y == 1 and in_grid, craftingData["pattern"][1][1])
			Visuals.drawItemFrame(11, 5, sel_x == 2 and sel_y == 1 and in_grid, craftingData["pattern"][1][2])
			Visuals.drawItemFrame(1, 8, sel_x == 0 and sel_y == 2 and in_grid, craftingData["pattern"][2][0])
			Visuals.drawItemFrame(6, 8, sel_x == 1 and sel_y == 2 and in_grid, craftingData["pattern"][2][1])
			Visuals.drawItemFrame(11, 8, sel_x == 2 and sel_y == 2 and in_grid, craftingData["pattern"][2][2])
			
			stdscr.addstr(6, 17, "=>")

			Visuals.drawItemFrame(20, 5, not in_grid, "#" if craftingData["result"] else "")
			stdscr.refresh()

		itemFrameGenerator()

		Visuals.drawLegend(craftingData["keys"])
		stdscr.refresh()

		key = stdscr.getch()
		if key == c.KEY_UP:
			sel_y = (sel_y -1) %3
		elif key == c.KEY_DOWN:
			sel_y = (sel_y +1) %3
		elif key == c.KEY_RIGHT:
			sel_x = (sel_x +1) %3
		elif key == c.KEY_LEFT:
			sel_x = (sel_x -1) %3
		elif key in (c.KEY_ENTER, 10, 13):
			if in_grid:
				all_keys: list[str] = []
				all_item_ids: list[str] = []
				for key in craftingData["keys"]:
					all_keys.append(key["key_name"])
					all_item_ids.append(key["item_id"])

				key_interaction: str = Visuals.optionBox(start_x, start_y, "Menu", "Set key", "Delete key", "New key", "Remove key", "Cancel")
				stdscr.refresh()
				
				if key_interaction == "Set key":
					selected_key: str = Visuals.optionBox(start_x, start_y, "Keys", *all_keys, "Cancel")
					stdscr.refresh()

					if selected_key == "Cancel" or selected_key is None:
						stdscr.refresh()
					else:
						craftingData["pattern"][sel_y][sel_x] = selected_key

				elif key_interaction == "Delete key":
					key_deletion_interaction: str = Visuals.optionBox(start_x, start_y, "Are you sure?", "Yes", "No")
					if key_deletion_interaction == "Yes":
						craftingData["pattern"][sel_y][sel_x] = ""

				elif key_interaction == "New key":
					new_key: str = Visuals.inputBox(start_x, start_y, "Type key name", "", 2)
					if new_key is None or len(new_key) != 1:
						Visuals.optionBox(start_x, start_y, "Key value must be 1 character long", "Ok")
						stdscr.refresh()

					if new_key in all_keys:
						Visuals.optionBox(start_x, start_y, "Key already exists", "Ok")
						stdscr.refresh()
					
					if not (new_key is None or new_key in all_keys):
						new_item_id: str = Visuals.inputBox(start_x, start_y, "Type item ID", "")
						if new_item_id in all_item_ids:
							Visuals.optionBox(start_x, start_y, "Item already exists", "Ok")
							stdscr.refresh()

						if new_item_id is None:
							Visuals.optionBox(start_x, start_y, "No item ID provided", "Ok")
							stdscr.refresh()

						if not (new_item_id is None or new_item_id in all_item_ids):
							craftingData["keys"].append({"key_name": new_key, "item_id": new_item_id})
							Visuals.optionBox(start_x, start_y, f"Added key {new_key}", "Ok")
							Visuals.drawLegend(craftingData["keys"])

				elif key_interaction == "Remove key":
					key_to_remove: str = Visuals.optionBox(start_x, start_y, key_interaction, *all_keys, "Cancel")
					if key_to_remove == "Cancel":
						stdscr.refresh()
					else:
						key_remove_interaction: str = Visuals.optionBox(start_x, start_y, "Are you sure?", "Yes", "No")
						if key_remove_interaction == "Yes":
							for key in craftingData["keys"]:
								if key["key_name"] == key_to_remove:
									craftingData["keys"].remove(key)
									itemFrameGenerator()

							for r_num, row in enumerate(craftingData["pattern"]):
								for c_num, char in enumerate(row):
									if char == key_to_remove:
										craftingData["pattern"][r_num][c_num] = ""

							Visuals.drawLegend(craftingData["keys"])
							stdscr.refresh()
			else:
				result_option: str = Visuals.optionBox(start_x,	start_y, "Result", "Set item", "Set amount", "Set category (optional)", "Save")
				if result_option == "Set item":
					result_item: str = Visuals.inputBox(start_x, start_y, "Type item name", "")
					if not result_item or result_item is None:
						Visuals.optionBox(start_x, start_y, "No item name", "Ok")
						stdscr.refresh()
					else:
						Visuals.optionBox(start_x, start_y, "Item name set", "Ok")
						craftingData["result"]["item_id"] = result_item
						stdscr.refresh()
				elif result_option == "Set amount":
					result_item_count_interaction: str = Visuals.inputBox(start_x, start_y, "Set amount", "", 3)
					try:
						result_item_count: int = int(result_item_count_interaction)
						if not (result_item_count > 0 and result_item_count <= 64):
							Visuals.optionBox(start_x, start_y, "Result must be between 1 and 64!", "Ok")
							stdscr.refresh()
						else:
							craftingData["result"]["count"] = result_item_count

					except ValueError:
						Visuals.optionBox(start_x, start_y, "Result must be a number!")
						stdscr.refresh()

				elif result_option == "Set category (optional)":
					result_item_category: str = Visuals.inputBox(start_x, start_y, "Set category", "")
					if result_item_category:
						craftingData["category"] = result_item_category
					else:
						Visuals.optionBox(start_x, start_y, "No item category set", "Ok")
						stdscr.refresh()

				elif result_option == "Save":
					save_interaction: str = Visuals.optionBox(start_x, start_y, "Save", "Save to file", "Generate Datapack")
					stdscr.refresh()

					file_result_name: str = Visuals.inputBox(start_x, start_y, "Type file name", "")
					if file_result_name.strip() == "" or file_result_name is None:
						Visuals.optionBox(start_x, start_y, "Type file name", "Ok")
						stdscr.refresh()
					else:
						file_result: dict = {}
						file_result["type"] = "minecraft:crafting_shaped"

						if craftingData["category"].strip() != "":
							file_result["category"] = result_item_category

						all_keys: list[str] = []
						all_item_ids: list[str] = []
						for key in craftingData["keys"]:
							all_keys.append(key["key_name"])
							all_item_ids.append(key["item_id"])

						used_keys: list = []
						for row in craftingData["pattern"]:
							for char in row:
								if char in all_keys:
									used_keys.append(char)

						keys: list = craftingData["keys"]
						for key in craftingData["keys"]:
							if key["key_name"] not in used_keys:
								keys.remove(key)

						craftingData["keys"] == keys
						file_result["key"] = {}

						for key in craftingData["keys"]:
							file_result["key"][key["key_name"]] = key["item_id"]

						crafting_pattern: list = craftingData["pattern"]

						non_empty_rows = [
							i for i, row in enumerate(crafting_pattern)
							if any(cell for cell in row)
						]
						if not non_empty_rows:
							result_pattern = []
						else:
							min_row, max_row = min(non_empty_rows), max(non_empty_rows)

							num_cols = len(crafting_pattern[0])
							non_empty_cols = [
								j for j in range(num_cols)
								if any(crafting_pattern[i][j] for i in range(len(crafting_pattern)))
							]
							min_col, max_col = min(non_empty_cols), max(non_empty_cols)

							result_pattern = []
							for i in range(min_row, max_row + 1):
								row = crafting_pattern[i][min_col:max_col + 1]
								result_pattern.append("".join(cell if cell else " " for cell in row))

						file_result["pattern"] = result_pattern

						file_result["result"] = {}

						file_result["result"]["id"] = craftingData["result"]["item_id"]
						file_result["result"]["count"] = craftingData["result"]["count"]

						if save_interaction == "Save to file":
							current_location: str = os.getcwd()
							with open (f"{current_location}/{file_result_name}.json", "w") as f:
								json.dump(file_result, f, indent=4)

						elif save_interaction == "Generate Datapack":
							current_location: str = os.getcwd()
							os.mkdir("Generated Datapack") ; os.chdir("Generated Datapack")
							with open ("pack.mcmeta", "w") as f:
								pack_mcmeta_content: dict = {
									"pack": {
										"pack_format": 48,
										"description": "Custom crafting (made my MCUtils by @furry_onko)"
									}
								}
								json.dump(pack_mcmeta_content, f, indent=2)

							os.mkdir("data")               ; os.chdir("data")
							os.mkdir("minecraft")          ; os.chdir("minecraft")
							os.mkdir("recipe")             ; os.chdir("recipe")
							with open (f"{file_result_name}.json", "w") as f:
								json.dump(file_result, f, indent=4)
		elif key == 9:
			in_grid = not in_grid
			itemFrameGenerator()

		stdscr.refresh()

def craftingShapeless(stdscr, start_x: int, start_y: int) -> None:
	...

def menu(stdscr) -> None:
	c.start_color()
	c.init_pair(1, c.COLOR_WHITE, c.COLOR_BLACK)
	c.init_pair(2, c.COLOR_BLACK, c.COLOR_WHITE)
	c.init_pair(3, c.COLOR_MAGENTA, c.COLOR_BLACK)

	height, width = stdscr.getmaxyx()
	pop_height, pop_width = 12, 75
	start_x: int = width // 2 - pop_width // 2
	start_y: int = height// 2 - pop_height// 2

	in_select_menu: bool = True

	c.curs_set(0)

	stdscr.clear()
	stdscr.refresh()
	stdscr.keypad(True)

	craftingOptions: list[str] = ["Crafting", "Smelting", "Blasting", "Campfire", "Smoking", "Stonecutter", "Smithing table", "Exit"]
	sel_craftingOptions: int = 0
	craftingOptionsPop = c.newwin(pop_height, pop_width, start_y, start_x)
	craftingOptionsPop.keypad(True)
	mode: str = ""

	while in_select_menu:
		craftingOptionsPop.clear()
		craftingOptionsPop.box()
		craftingOptionsPop.addstr(1, 2, "Select Option")
		
		for index, option in enumerate(craftingOptions):
			position: int = index +3
			if index == sel_craftingOptions:
				craftingOptionsPop.addstr(position, 2, option, c.color_pair(2))
			else:
				craftingOptionsPop.addstr(position, 2, option, c.color_pair(1))

		key = craftingOptionsPop.getch()

		if key == c.KEY_UP:
			sel_craftingOptions = (sel_craftingOptions -1) % len(craftingOptions)
		elif key == c.KEY_DOWN:
			sel_craftingOptions = (sel_craftingOptions +1) % len(craftingOptions)
		elif key in (c.KEY_ENTER, 10, 13):
			craftingOptionsPop.clear()
			craftingOptionsPop.refresh()
			mode = craftingOptions[sel_craftingOptions]
			in_select_menu = False

	if mode == "Crafting":
		crafting_selection_interaction: str = Visuals.optionBox(start_x, start_y, "Select crafting type", "Shaped", "Shapeless", "Back")
		if crafting_selection_interaction == "Shaped":
			craftingShaped(stdscr, start_x, start_y)
		elif crafting_selection_interaction == "Shapeless":
			craftingShapeless(stdscr, start_x, start_y)
		else:
			main()

	else:
		exit(0)

def main() -> None:
	c.wrapper(menu)

if __name__ == "__main__": main()