import React, { useState, useRef } from "react";
import { transcribeSpeech } from "../../lib/api";
import { useLanguage } from "../../lib/LanguageContext";

interface VoiceInputButtonProps {
  onTranscription: (text: string) => void;
}

export const VoiceInputButton: React.FC<VoiceInputButtonProps> = ({ onTranscription }) => {
  const { lang, t } = useLanguage();
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const [pendingText, setPendingText] = useState<string>("");
  const [showConfirm, setShowConfirm] = useState(false);

  const startRecording = async () => {
    setErrorMsg(null);
    setPendingText("");
    setShowConfirm(false);
    audioChunksRef.current = [];
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        await handleTranscribe(audioBlob);
        // Stop all tracks in stream
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setRecording(true);
    } catch (e: any) {
      setErrorMsg(t("Microphone permission denied or unsupported audio hardware."));
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const handleTranscribe = async (blob: Blob) => {
    setLoading(true);
    setErrorMsg(null);

    try {
      const res = await transcribeSpeech(blob, lang);
      if (res.status === "SUCCESS" && res.text) {
        setPendingText(res.text);
        setShowConfirm(true);
      } else {
        setErrorMsg(t("Voice transcription failed. Please try again."));
      }
    } catch (e: any) {
      setErrorMsg(t("Voice transcription failed. Please try again."));
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = () => {
    if (pendingText.trim()) {
      onTranscription(pendingText);
    }
    setShowConfirm(false);
    setPendingText("");
  };

  return (
    <div className="flex flex-col items-start gap-2 border border-slate-100 p-2.5 rounded-lg bg-slate-50/50 w-full">
      <div className="flex items-center gap-2">
        {recording ? (
          <button
            type="button"
            onClick={stopRecording}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-red-100 text-red-700 hover:bg-red-200 animate-pulse text-sm font-medium rounded-md min-h-[40px] focus:ring-2 focus:ring-red-500"
            aria-label={t("Stop recording")}
          >
            <span className="w-2.5 h-2.5 bg-red-600 rounded-full animate-ping"></span>
            {t("Stop Recording")}
          </button>
        ) : (
          <button
            type="button"
            onClick={startRecording}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50 text-sm font-medium rounded-md min-h-[40px] focus:ring-2 focus:ring-gray-500"
            aria-label={t("Speak instead")}
          >
            <span>🎙</span>
            {loading ? t("Transcribing...") : t("Speak instead")}
          </button>
        )}
      </div>

      {showConfirm && (
        <div className="mt-2 p-3 bg-white border border-slate-200 rounded-lg flex flex-col gap-2 w-full max-w-md shadow-sm">
          <label className="block text-xs font-bold text-slate-500 uppercase">{t("Verify Spoken Transcription")}</label>
          <textarea
            className="w-full p-2 border border-slate-200 rounded-md text-sm bg-white"
            rows={3}
            value={pendingText}
            onChange={(e) => setPendingText(e.target.value)}
          />
          <div className="flex justify-end gap-2 mt-1">
            <button
              type="button"
              onClick={() => { setShowConfirm(false); setPendingText(""); }}
              className="px-3 py-1.5 bg-slate-50 text-slate-600 hover:bg-slate-100 text-xs font-semibold rounded"
            >
              {t("Cancel")}
            </button>
            <button
              type="button"
              onClick={handleConfirm}
              className="px-3 py-1.5 bg-indigo-650 hover:bg-indigo-700 text-white text-xs font-semibold rounded"
            >
              {t("Confirm & Insert")}
            </button>
          </div>
        </div>
      )}

      {errorMsg && (
        <span className="text-xs text-red-500 mt-1 font-medium" role="alert">
          {errorMsg}
        </span>
      )}
    </div>
  );
};
