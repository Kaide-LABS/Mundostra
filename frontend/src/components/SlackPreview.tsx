'use client';

interface Props {
  text: string;
  slackTs?: string | null;
}

export function SlackPreview({ text, slackTs }: Props) {
  return (
    <div className="rounded-lg border border-white/5 bg-[#1a1d21] p-3">
      <div className="mb-2 flex items-center gap-2">
        <div className="flex h-5 w-5 items-center justify-center rounded bg-[#4A154B]">
          <span className="text-[10px] font-bold text-white">S</span>
        </div>
        <span className="text-xs font-semibold text-gray-300">Mundostra Travel OS</span>
        <span className="text-[10px] text-gray-600">BOT</span>
        {slackTs && (
          <span className="ml-auto rounded bg-green-500/10 px-1.5 py-0.5 text-[10px] text-green-400">
            Sent to Slack
          </span>
        )}
      </div>
      <p className="text-sm leading-relaxed text-gray-400">{text}</p>
    </div>
  );
}
