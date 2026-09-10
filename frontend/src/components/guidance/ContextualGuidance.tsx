import React, { useState, useEffect } from "react";
import { fetchGuidance } from "../../lib/api";
import { useLanguage } from "../../lib/LanguageContext";
import { ListenButton } from "./ListenButton";

interface ContextualGuidanceProps {
  context: string;
}

export const ContextualGuidance: React.FC<ContextualGuidanceProps> = ({ context }) => {
  const { lang, t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<{
    title: string;
    instruction: string;
    why_required: string;
    what_happens_next: string;
    warning: string;
  } | null>(null);

  useEffect(() => {
    if (isOpen && !data) {
      setLoading(true);
      fetchGuidance(context, lang)
        .then((res) => setData(res))
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [isOpen, context, lang, data]);

  // Reset loaded data if language changes
  useEffect(() => {
    setData(null);
  }, [lang]);

  return (
    <div className="border border-blue-100 bg-blue-50/30 rounded-lg p-3 my-3">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left text-sm font-semibold text-blue-800 hover:text-blue-900 focus:outline-none min-h-[44px] focus:ring-2 focus:ring-blue-500 rounded-md px-2"
        aria-expanded={isOpen}
      >
        <span className="flex items-center gap-2">
          <span>ℹ</span>
          {t("Need help understanding this step?")}
        </span>
        <span>{isOpen ? "▲" : "▼"}</span>
      </button>

      {isOpen && (
        <div className="mt-3 pt-3 border-t border-blue-100 flex flex-col gap-3">
          {loading ? (
            <div className="text-sm text-gray-500">{t("Loading guidance...")}</div>
          ) : data ? (
            <div className="flex flex-col gap-2.5">
              <h4 className="text-sm font-bold text-blue-950">{data.title}</h4>
              <div>
                <span className="text-xs font-bold text-blue-800 uppercase block">
                  {t("What should I do?")}
                </span>
                <p className="text-sm text-gray-700">{data.instruction}</p>
              </div>
              <div>
                <span className="text-xs font-bold text-blue-800 uppercase block">
                  {t("Why is this required?")}
                </span>
                <p className="text-sm text-gray-700">{data.why_required}</p>
              </div>
              <div>
                <span className="text-xs font-bold text-blue-800 uppercase block">
                  {t("What happens next?")}
                </span>
                <p className="text-sm text-gray-700">{data.what_happens_next}</p>
              </div>
              {data.warning && (
                <div className="bg-yellow-50 border border-yellow-200 rounded p-2 text-xs text-yellow-800">
                  <strong>{t("Warning")}: </strong>
                  {data.warning}
                </div>
              )}

              <div className="mt-2 pt-2 border-t border-blue-50">
                <ListenButton
                  textToSpeak={`${data.title}. ${data.instruction}. ${data.why_required}. ${data.what_happens_next}`}
                />
              </div>
            </div>
          ) : (
            <div className="text-sm text-red-500">{t("Guidance is currently unavailable.")}</div>
          )}
        </div>
      )}
    </div>
  );
};
