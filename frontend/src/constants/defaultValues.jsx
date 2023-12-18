export const UserRole = {
  Admin: 0,
  Editor: 1,
};
/*
Menu Types:
"menu-default", "menu-sub-hidden", "menu-hidden"
*/
export const defaultMenuType = "menu-default";

export const subHiddenBreakpoint = 1440;
export const menuHiddenBreakpoint = 768;
export const defaultLocale = "en";
export const localeOptions = [
  { id: "en", name: "English - LTR", direction: "ltr" },
  { id: "es", name: "Español", direction: "ltr" },
  { id: "enrtl", name: "English - RTL", direction: "rtl" },
];

export const adminRoot = "/mirror";
export const searchPath = `${adminRoot}/#`;

export const themeColorStorageKey = "__theme_selected_color";
export const isMultiColorActive = true;
export const defaultColor = "dark.redruby";
export const isDarkSwitchActive = true;
export const defaultDirection = "ltr";
export const themeRadiusStorageKey = "__theme_radius";
export const isAuthGuardActive = false;
export const colors = [
  "bluenavy",
  "blueyale",
  "blueolympic",
  "greenmoss",
  "greenlime",
  "purplemonster",
  "orangecarrot",
  "redruby",
  "yellowgranola",
  "greysteel",
];
