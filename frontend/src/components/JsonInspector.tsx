'use client';

import { useState } from 'react';

function JsonValue({ value, depth }: { value: unknown; depth: number }) {
  const [open, setOpen] = useState(depth < 2);

  if (value === null) return <span className="text-gray-500">null</span>;
  if (value === undefined) return <span className="text-gray-500">undefined</span>;
  if (typeof value === 'boolean') return <span className="text-amber-600">{String(value)}</span>;
  if (typeof value === 'number') return <span className="text-cyan-700">{value}</span>;
  if (typeof value === 'string') {
    if (value.length > 200) {
      return <span className="text-green-700">&quot;{value.slice(0, 200)}...&quot;</span>;
    }
    return <span className="text-green-700">&quot;{value}&quot;</span>;
  }

  if (Array.isArray(value)) {
    if (value.length === 0) return <span className="text-gray-400">[]</span>;
    return (
      <span>
        <button onClick={() => setOpen(!open)} className="text-gray-500 hover:text-gray-900">
          {open ? '[ -' : `[${value.length} items +`}
        </button>
        {open && (
          <div className="ml-4 border-l border-gray-200 pl-2">
            {value.map((item, i) => (
              <div key={i} className="py-0.5">
                <span className="text-gray-500">{i}: </span>
                <JsonValue value={item} depth={depth + 1} />
              </div>
            ))}
          </div>
        )}
        {open && <span className="text-gray-400">]</span>}
      </span>
    );
  }

  if (typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>);
    if (entries.length === 0) return <span className="text-gray-400">{'{}'}</span>;
    return (
      <span>
        <button onClick={() => setOpen(!open)} className="text-gray-500 hover:text-gray-900">
          {open ? '{ -' : `{${entries.length} keys +`}
        </button>
        {open && (
          <div className="ml-4 border-l border-gray-200 pl-2">
            {entries.map(([key, val]) => (
              <div key={key} className="py-0.5">
                <span className="text-violet-700">{key}</span>
                <span className="text-gray-500">: </span>
                <JsonValue value={val} depth={depth + 1} />
              </div>
            ))}
          </div>
        )}
        {open && <span className="text-gray-400">{'}'}</span>}
      </span>
    );
  }

  return <span>{String(value)}</span>;
}

export function JsonInspector({ data }: { data: Record<string, unknown> | null }) {
  if (!data) return <span className="text-gray-500 text-xs">No data</span>;
  return (
    <div className="overflow-x-auto font-mono text-[11px] leading-relaxed sm:text-xs">
      <JsonValue value={data} depth={0} />
    </div>
  );
}
