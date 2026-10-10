exec("mods/AoDJPAddonProbe/tooltips.cs");
exec("./known_fonts.cs");
exec("mods/AoDJPAddonProbe/display.cs");

// Probe v4: fresh profile instances, preserving all inherited settings/sizes.
function AoDJPProbe_refreshControl(%control)
{
   if (%control.getClassName() $= "GuiControlProfile") return;
   AoDJPAddonProbe_localizeControl(%control);
   AoDJPTooltip_apply(%control);
   if (%control.getClassName() $= "GuiBitmapCtrl") AoDJPAddonProbe_replaceBitmap(%control);
   if (%control.getClassName() $= "GuiBitmapCtrl" || %control.getClassName() $= "GuiBitmapButtonCtrl" || %control.getClassName() $= "GuiBitmapButtonTextCtrl") AoDJPButtonImages_replaceBitmap(%control);
   if (%control.getClassName() $= "GuiBitmapCtrl" || %control.getClassName() $= "GuiBitmapButtonCtrl" || %control.getClassName() $= "GuiBitmapButtonTextCtrl") AoDJPRemainingImages_replaceBitmap(%control);
   if (isObject(%control.profile))
   {
      %original = %control.profile;
      if (isObject(%original))
      {
         %base = %original.getName();
         if (%base !$= "" && getSubStr(%base, 0, 15) !$= "AoDJPProbeFont_")
         {
            %fresh = "AoDJPProbeFont_" @ %base;
            if (!isObject(%fresh))
               eval("new GuiControlProfile(" @ %fresh @ " : " @ %base @ ") { fontType = \"BIZ UDPMincho Medium\"; };");
            if (isObject(%fresh)) { %control.setProfile(%fresh); AoDJPProbe_reparseText(%control); $AoDJPProbe::assigned++; }
         }
      }
   }
   if (%control.getClassName() $= "SimGroup" || %control.getClassName() $= "SimSet" || getSubStr(%control.getClassName(), 0, 3) $= "Gui" || getSubStr(%control.getClassName(), 0, 2) $= "fb")
      for (%i = 0; %i < %control.getCount(); %i++)
         AoDJPProbe_refreshControl(%control.getObject(%i));
}
function AoDJPProbe_refreshFonts()
{
   AoDJPProbe_applyKnownProfiles();
   $AoDJPProbe::assigned = 0;
   if (isObject(GuiData)) AoDJPProbe_refreshControl(GuiData);
   if (isObject(Canvas)) AoDJPProbe_refreshControl(Canvas);
   AoDJPAddonProbe_applyLabels();
   echo("AoDJPProbe v8: profiles reassigned = " @ $AoDJPProbe::assigned);
}

// Font-only module. Text, artwork, game rules and font sizes are not replaced.
function AoDJapaneseFont_apply()
{
   AoDJPProbe_applyKnownProfiles();
   %font = "BIZ UDPMincho Medium";
   if (isObject(GuiDefaultProfile)) GuiDefaultProfile.fontType = %font;
   if (isObject(GuiData))
   {
      for (%i = 0; %i < GuiData.getCount(); %i++)
      {
         %profile = GuiData.getObject(%i);
         if (%profile.getClassName() $= "GuiControlProfile")
            %profile.fontType = %font;
      }
   }
   // Refresh the NPC-name control's cached font, preserving stock layout.
   if (!isObject(AoDJPName17) && isObject(Candara_Autosize_17)) new GuiControlProfile(AoDJPName17 : Candara_Autosize_17) { fontType = "BIZ UDPMincho Medium"; };
   if (!isObject(AoDJPName20) && isObject(Candara_Autosize_20)) new GuiControlProfile(AoDJPName20 : Candara_Autosize_20) { fontType = "BIZ UDPMincho Medium"; };
   if (!isObject(AoDJPName22) && isObject(Candara_Autosize_22)) new GuiControlProfile(AoDJPName22 : Candara_Autosize_22) { fontType = "BIZ UDPMincho Medium"; };
   if (!isObject(AoDJPName24) && isObject(Candara_Autosize_24)) new GuiControlProfile(AoDJPName24 : Candara_Autosize_24) { fontType = "BIZ UDPMincho Medium"; };
   if (!isObject(AoDJPName32) && isObject(Candara_Autosize_32)) new GuiControlProfile(AoDJPName32 : Candara_Autosize_32) { fontType = "BIZ UDPMincho Medium"; };
   %height = getWord($pref::Video::mode, 1);
   %name = AoDJPName32;
   if (%height <= 600) %name = AoDJPName17;
   else if (%height <= 768) %name = AoDJPName20;
   else if (%height < 1080) %name = AoDJPName22;
   else if (%height < 1440) %name = AoDJPName24;
   if (isObject(DS_NPC_Name) && isObject(%name)) DS_NPC_Name.setProfile(%name);
   AoDJPProbe_refreshFonts();
   echo("AoDJapaneseFont: Japanese GUI profiles applied.");
}

package AoDJapaneseFontHooks
{
   function LoadLocalizableText()
   {
      %result = Parent::LoadLocalizableText();
      AoDJapaneseFont_apply();
      return %result;
   }
   function rescaleFonts()
   {
      %result = Parent::rescaleFonts();
      AoDJapaneseFont_apply();
      return %result;
   }
   function DialogueScreen::onWake(%this)
   {
      %result = Parent::onWake(%this);
      AoDJapaneseFont_apply();
      return %result;
   }
   function SS_showSlide(%slide)
   {
      %result = Parent::SS_showSlide(%slide);
      AoDJapaneseFont_apply();
      if (isObject(Canvas)) AoDJPProbe_refreshControl(Canvas);
      schedule(0, 0, "AoDJPProbe_refreshFonts");
      return %result;
   }
   function LoadingGui::onWake(%this)
   {
      %result = Parent::onWake(%this);
      // Translate the generic initial label; do not replace progress messages.
      if (isObject(LoadingProgressTxt))
      {
         %text = LoadingProgressTxt.getValue();
         if (%text $= "Loading..." || %text $= "Loading ..." || %text $= "")
            LoadingProgressTxt.setValue("読み込み中…");
      }
      AoDJPProbe_refreshFonts();
      if (isObject(LoadingProgressTxt)) AoDJPProbe_refreshControl(LoadingProgressTxt);
      return %result;
   }
};

function AoDJapaneseFont::create()
{
   addGameFont("C:/Windows/Fonts/BIZ-UDMinchoM.ttc");
   AoDJPProbe_prepareKnownFonts();
   activatePackage(AoDJapaneseFontHooks);
   activatePackage(AoDJPAddonProbeScreenHooks);
   activatePackage(AoDJPProbeLoadingHooks);
   AoDJapaneseFont_apply();
}
function AoDJapaneseFont::destroy()
{
   deactivatePackage(AoDJPProbeLoadingHooks);
   deactivatePackage(AoDJPAddonProbeScreenHooks);
   deactivatePackage(AoDJapaneseFontHooks);
}

package AoDJPAddonProbeScreenHooks {
   function StartupGui::next(%this) {
      %this.logo2 = "mods/AoDJPAddonProbe/images/decadenceQuote_ja.png";
      return Parent::next(%this);
   }

   function SlideType0::onWake(%this) { %result = Parent::onWake(%this); AoDJPProbe_refreshControl(%this); schedule(0, 0, "AoDJPProbe_refreshControl", %this); return %result; }
   function SlideType1::onWake(%this) { %result = Parent::onWake(%this); AoDJPProbe_refreshControl(%this); schedule(0, 0, "AoDJPProbe_refreshControl", %this); return %result; }
   function SlideType2::onWake(%this) { %result = Parent::onWake(%this); AoDJPProbe_refreshControl(%this); schedule(0, 0, "AoDJPProbe_refreshControl", %this); return %result; }
   function SlideType3::onWake(%this) { %result = Parent::onWake(%this); AoDJPProbe_refreshControl(%this); schedule(0, 0, "AoDJPProbe_refreshControl", %this); return %result; }
   function SlideType4::onWake(%this) { %result = Parent::onWake(%this); AoDJPProbe_refreshControl(%this); schedule(0, 0, "AoDJPProbe_refreshControl", %this); return %result; }
   function SlideType5::onWake(%this) { %result = Parent::onWake(%this); AoDJPProbe_refreshControl(%this); schedule(0, 0, "AoDJPProbe_refreshControl", %this); return %result; }
   function SlideType6::onWake(%this) { %result = Parent::onWake(%this); AoDJPProbe_refreshControl(%this); schedule(0, 0, "AoDJPProbe_refreshControl", %this); return %result; }
   function Difficulty::onWake(%this) {
      %result = Parent::onWake(%this);
      AoDJPProbe_refreshControl(%this);
      schedule(0, 0, "AoDJPProbe_refreshControl", %this);
      return %result;
   }
   function loadStartup() {
      %result = Parent::loadStartup();
      if (isObject(StartupGui)) StartupGui.logo2 = "mods/AoDJPAddonProbe/images/decadenceQuote_ja.png";
      return %result;
   }

   function TutorialOverlay::onWake(%this) {
      AoDJPProbe_applyKnownProfiles();
      Parent::onWake(%this);
      AoDJPProbe_refreshFonts();
      schedule(0, 0, "AoDJPProbe_refreshFonts");
   }
   function InventoryScreen::onWake(%this) {
      AoDJPProbe_applyKnownProfiles();
      Parent::onWake(%this);
      AoDJPProbe_refreshFonts();
      schedule(0, 0, "AoDJPProbe_refreshFonts");
   }
   function AlchemyScreen::onWake(%this) {
      AoDJPProbe_applyKnownProfiles();
      Parent::onWake(%this);
      AoDJPProbe_refreshFonts();
      schedule(0, 0, "AoDJPProbe_refreshFonts");
   }
   function CraftScreen::onWake(%this) {
      AoDJPProbe_applyKnownProfiles();
      Parent::onWake(%this);
      AoDJPProbe_refreshFonts();
      schedule(0, 0, "AoDJPProbe_refreshFonts");
   }
   function CharScreen::onWake(%this) {
      Parent::onWake(%this);
      if (isObject(CS_bg)) CS_bg.setBitmap("mods/AoDJPAddonProbe/images/character_screen_panel_1080_ja.png");
      AoDJPProbe_refreshControl(%this);
      schedule(0, 0, "AoDJPProbe_refreshControl", %this);
   }
   function CharacterScreen::onWake(%this) {
      AoDJPProbe_applyKnownProfiles();
      Parent::onWake(%this);
      AoDJPProbe_refreshFonts();
      schedule(0, 0, "AoDJPProbe_refreshFonts");
   }
   function JournalScreen::onWake(%this) {
      AoDJPAddonProbe_applyJournal();
      AoDJPProbe_applyKnownProfiles();
      Parent::onWake(%this);
      AoDJPProbe_refreshFonts();
      schedule(0, 0, "AoDJPProbe_refreshFonts");
   }
   function MapScreen::onWake(%this) {
      AoDJPProbe_applyKnownProfiles();
      Parent::onWake(%this);
      AoDJPProbe_refreshFonts();
      schedule(0, 0, "AoDJPProbe_refreshFonts");
   }
   function LootScreen::onWake(%this) {
      AoDJPProbe_applyKnownProfiles();
      Parent::onWake(%this);
      AoDJPProbe_refreshFonts();
      schedule(0, 0, "AoDJPProbe_refreshFonts");
   }
   function TradeScreen::onWake(%this) {
      AoDJPProbe_applyKnownProfiles();
      Parent::onWake(%this);
      AoDJPProbe_refreshFonts();
      schedule(0, 0, "AoDJPProbe_refreshFonts");
   }
   function PlayGui::onWake(%this) {
      AoDJPProbe_applyKnownProfiles();
      Parent::onWake(%this);
      AoDJPProbe_refreshFonts();
      schedule(0, 0, "AoDJPProbe_refreshFonts");
   }
   function MainMenuGui::onWake(%this) {
      AoDJPProbe_applyKnownProfiles();
      Parent::onWake(%this);
      AoDJPProbe_refreshFonts();
      schedule(0, 0, "AoDJPProbe_refreshFonts");
   }
   function OptionsDlg::onWake(%this) {
      AoDJPProbe_applyKnownProfiles();
      Parent::onWake(%this);
      AoDJPProbe_refreshFonts();
      schedule(0, 0, "AoDJPProbe_refreshFonts");
   }
   function TO_Show() { Parent::TO_Show(); AoDJPProbe_refreshFonts(); schedule(0, 0, "AoDJPProbe_refreshFonts"); }
};

function AoDJPProbe_fixLoadingTags() {
   if (isObject(LoadingGui)) {
      for (%i = 0; %i < LoadingGui.qLineCount; %i++)
         LoadingGui.qLine[%i] = strreplace(LoadingGui.qLine[%i], "<font:Pegasus:", "<font:BIZ UDPMincho Medium:");
   }
   if (isObject(LoadingProgressTxt)) AoDJPProbe_refreshControl(LoadingProgressTxt);
}
package AoDJPProbeLoadingHooks {
   function handleLoadDescriptionMessage(%a, %b, %c) {
      Parent::handleLoadDescriptionMessage(%a, %b, %c);
      AoDJPProbe_fixLoadingTags();
   }
   function handleLoadInfoDoneMessage(%a, %b) {
      AoDJPProbe_fixLoadingTags();
      Parent::handleLoadInfoDoneMessage(%a, %b);
      AoDJPProbe_refreshFonts();
   }
};
