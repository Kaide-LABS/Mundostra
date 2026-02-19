'use client';

interface Props {
  text: string;
  teamsSent?: boolean;
}

export function TeamsPreview({ text, teamsSent }: Props) {
  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
      <div className="mb-2 flex items-center gap-2">
        <div className="flex h-5 w-5 items-center justify-center rounded bg-[#6264A7]">
          <span className="text-[10px] font-bold text-white">T</span>
        </div>
        <span className="text-xs font-semibold text-gray-800">Mundostra Travel OS</span>
        <span className="text-[10px] text-gray-400">BOT</span>
        {teamsSent && (
          <span className="ml-auto rounded bg-green-100 px-1.5 py-0.5 text-[10px] text-green-700">
            Sent to Teams
          </span>
        )}
      </div>
      <p className="text-sm leading-relaxed text-gray-600">{text}</p>
    </div>
  );
}
