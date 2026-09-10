import React, { useState } from "react";
import { synthesizeSpeech } from "../../lib/api";
import { useLanguage } from "../../lib/LanguageContext";

interface ListenButtonProps {
  textToSpeak: string;
}

export const ListenButton: React.FC<ListenButtonProps> = ({ textToSpeak }) => {
  const { lang, t } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [audioObj, setAudioObj] = useState<HTMLAudioElement | null>(null);

  const handleSpeak = async () => {
    if (audioObj) {
      audioObj.currentTime = 0;
      audioObj.play();
      return;
    }

    setLoading(true);
    setErrorMsg(null);

    try {
      const res = await synthesizeSpeech(textToSpeak, lang);
      if (res.status === "OFFLINE" || !res.audio_content_base64) {
        setErrorMsg(t("Audio guidance is currently unavailable."));
      } else {
        const audioSrc = `data:audio/wav;base64,${res.audio_content_base64}`;
        const audio = new Audio(audioSrc);
        setAudioObj(audio);
        audio.play();
      }
    } catch (e: any) {
      setErrorMsg(t("Audio guidance is currently unavailable."));
    } finally {
      setLoading(false);
    }
  };

  const handleStop = () => {
    if (audioObj) {
      audioObj.pause();
    }
  };

  return (
    <div className="inline-flex flex-col items-start gap-1">
      <div className="flex items-center gap-2">
        <button
          onClick={handleSpeak}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 disabled:opacity-50 text-sm font-medium rounded-md min-h-[40px] focus:ring-2 focus:ring-blue-500"
          aria-label={t("Listen to explanation")}
        >
          <span>🔊</span>
          {loading ? t("Generating audio...") : t("Listen")}
        </button>
        {audioObj && (
          <button
            onClick={handleStop}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 text-gray-700 hover:bg-gray-100 text-sm font-medium rounded-md min-h-[40px] focus:ring-2 focus:ring-gray-500"
            aria-label={t("Stop audio")}
          >
            <span>⏹</span>
            {t("Stop")}
          </button>
        )}
      </div>
      {errorMsg && (
        <span className="text-xs text-red-500 mt-1 font-medium" role="alert">
          {errorMsg}
        </span>
      )}
    </div>
  );
};
