// Font-only module. Text, artwork, game rules and font sizes are not replaced.
function AoDJapaneseFont_apply()
{
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
      AoDJapaneseFont_apply();
      return Parent::SS_showSlide(%slide);
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
      return %result;
   }
};

function AoDJapaneseFont::create()
{
   activatePackage(AoDJapaneseFontHooks);
   AoDJapaneseFont_apply();
}
function AoDJapaneseFont::destroy()
{
   deactivatePackage(AoDJapaneseFontHooks);
}
