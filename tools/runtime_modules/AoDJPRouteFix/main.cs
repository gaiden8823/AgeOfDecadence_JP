// Narrow display-path repairs. No dialogue, gameplay or layout changes.
function AoDJPRouteFix_refreshWarning() {
   if (isFunction("AoDJPProbe_applyKnownProfiles")) AoDJPProbe_applyKnownProfiles();
   if (isObject(MBOKTitle) && isFunction("AoDJPProbe_refreshControl")) AoDJPProbe_refreshControl(MBOKTitle);
   if (isObject(MBOKText) && isFunction("AoDJPProbe_refreshControl")) AoDJPProbe_refreshControl(MBOKText);
}
function AoDJPRouteFix_applyDifficulty(%control) {
   if (%control.getClassName() $= "GuiBitmapCtrl") {
      %name = fileBase(%control.getFieldValue("bitmap"));
      if (%name $= "difficulty_600" || %name $= "difficulty_768" || %name $= "difficulty_900" || %name $= "difficulty_1080" || %name $= "difficulty_1440")
         %control.setBitmap("mods/AoDJPAddonProbe/images/difficulty_1080_ja.png");
   }
   if (getSubStr(%control.getClassName(), 0, 3) $= "Gui" || getSubStr(%control.getClassName(), 0, 2) $= "fb")
      for (%i = 0; %i < %control.getCount(); %i++) AoDJPRouteFix_applyDifficulty(%control.getObject(%i));
}
function AoDJPRouteFix_refreshDifficulty() {
   if (isObject(Difficulty)) AoDJPRouteFix_applyDifficulty(Difficulty);
}
exec("./names.cs");
exec("./display_routes.cs");
exec("./map_field_drafts.cs");
// Update presentation names only; never setName, IDs, datablocks or character database.
function AoDJPRouteFix_refreshNameTree(%object, %depth) {
   if (!isObject(%object) || %depth > 32 || $AoDJPRouteFix_nameBudget <= 0) return;
   $AoDJPRouteFix_nameBudget--;
   // Dynamic display fields only; internal object names and datablocks are untouched.
   %fields = "contName cursorText modelObjectName";
   for (%fieldIndex = 0; %fieldIndex < 3; %fieldIndex++) {
      %field = getWord(%fields, %fieldIndex);
      %before = %object.getFieldValue(%field);
      %after = AoDJPRouteFix_translateMapField(AoDJPRouteFix_translateDisplay(%before));
      if (%before !$= %after) %object.setFieldValue(%field, %after);
   }
   if (%object.isMethod("getShapeName") && %object.isMethod("setShapeName")) {
      %before = %object.getShapeName();
      %after = AoDJPRouteFix_translateName(%before);
      if (%before !$= %after) %object.setShapeName(%after);
   }
   if (%object.isMethod("getCount") && %object.isMethod("getObject"))
      for (%i = 0; %i < %object.getCount(); %i++) AoDJPRouteFix_refreshNameTree(%object.getObject(%i), %depth + 1);
}
function AoDJPRouteFix_refreshNames() {
   $AoDJPRouteFix_nameBudget = 10000;
   if (isObject(MissionGroup)) AoDJPRouteFix_refreshNameTree(MissionGroup, 0);
   if (isObject(ServerGroup)) AoDJPRouteFix_refreshNameTree(ServerGroup, 0);
}

package AoDJPRouteFixHooks {
   function sayPhrase(%id, %text) {
      return Parent::sayPhrase(%id, AoDJPRouteFix_translateDisplay(%text));
   }
   function narratePhrase(%text) {
      return Parent::narratePhrase(AoDJPRouteFix_translateDisplay(%text));
   }
   function jsSetQuestName(%text) {
      return Parent::jsSetQuestName(AoDJPRouteFix_translateDisplay(%text));
   }
   function jsSetQuestStatus(%text) {
      return Parent::jsSetQuestStatus(AoDJPRouteFix_translateDisplay(%text));
   }

   function dlgCreateCharacter(%name, %id, %base, %a, %b, %c, %direction) {
      %result = Parent::dlgCreateCharacter(AoDJPRouteFix_translateName(%name), %id, %base, %a, %b, %c, %direction);
      cancel($AoDJPRouteFix_nameSchedule);
      $AoDJPRouteFix_nameSchedule = schedule(0, 0, "AoDJPRouteFix_refreshNames");
      return %result;
   }
   function LoadingGui::onSleep(%this) {
      %result = Parent::onSleep(%this);
      schedule(250, 0, "AoDJPRouteFix_refreshNames");
      return %result;
   }

   function MessageBoxOK(%title, %message, %callback) {
      if (isFunction("AoDJPProbe_applyKnownProfiles")) AoDJPProbe_applyKnownProfiles();
      %result = Parent::MessageBoxOK(%title, %message, %callback);
      AoDJPRouteFix_refreshWarning();
      schedule(0, 0, "AoDJPRouteFix_refreshWarning");
      return %result;
   }
   function Difficulty::onWake(%this) {
      %result = Parent::onWake(%this);
      AoDJPRouteFix_refreshDifficulty();
      schedule(0, 0, "AoDJPRouteFix_refreshDifficulty");
      return %result;
   }
};
function AoDJPRouteFix::create() { activatePackage(AoDJPRouteFixHooks); if (isFunction("AoDJPProbe_refreshFonts")) AoDJPProbe_refreshFonts(); }
function AoDJPRouteFix::destroy() { deactivatePackage(AoDJPRouteFixHooks); }
