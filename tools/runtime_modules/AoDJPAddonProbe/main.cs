function AoDJPAddonProbe_applyJournal() {
   exec("mods/AoDJPAddonProbe/journal/artefacts.english.cs");
   exec("mods/AoDJPAddonProbe/journal/characters.english.cs");
   exec("mods/AoDJPAddonProbe/journal/factions.english.cs");
   exec("mods/AoDJPAddonProbe/journal/locations.english.cs");
   exec("mods/AoDJPAddonProbe/journal/lore.english.cs");
   exec("mods/AoDJPAddonProbe/journal/quests.english.cs");
   exec("mods/AoDJPAddonProbe/journal/techniques.english.cs");
}
exec("./display.cs");
addDialogueFolder("dialogues/");
addLocalizableItemText("itemtext.*.xml");
function AoDJPAddonProbe_applyText() {
   AoDJPAddonProbe_applyJournal();
   exec("mods/AoDJPAddonProbe/text/char_screen.english.cs");
   exec("mods/AoDJPAddonProbe/text/character.english.cs");
   exec("mods/AoDJPAddonProbe/text/craft.english.cs");
   exec("mods/AoDJPAddonProbe/text/inventory_screen.english.cs");
   exec("mods/AoDJPAddonProbe/text/item_desc.english.cs");
   exec("mods/AoDJPAddonProbe/text/options.english.cs");
   exec("mods/AoDJPAddonProbe/text/phrases.english.cs");
   exec("mods/AoDJPAddonProbe/text/ranks.english.cs");
   exec("mods/AoDJPAddonProbe/text/text_vars.english.cs");
   exec("mods/AoDJPAddonProbe/text/textbox.english.cs");
   exec("mods/AoDJPAddonProbe/text/tutorial.english.cs");
   exec("mods/AoDJPAddonProbe/text/ui.english.cs");
   exec("mods/AoDJPAddonProbe/text/vco_cursor_text.english.cs");
   echo("AoDJPAddonProbe: text overrides loaded from mods only.");
}
package AoDJPAddonProbeHooks {
   function LoadLocalizableText() {
      %result = Parent::LoadLocalizableText();
      AoDJPAddonProbe_applyText();
      return %result;
   }
};
function AoDJPAddonProbe::create() { activatePackage(AoDJPAddonProbeHooks); AoDJPAddonProbe_applyText(); AoDJPAddonProbe_registerVisibleName(); AoDJPAddonProbe_applyLabels(); echo("AoDJPAddonProbe: enabled v4"); }
function AoDJPAddonProbe::destroy() { deactivatePackage(AoDJPAddonProbeHooks); }
