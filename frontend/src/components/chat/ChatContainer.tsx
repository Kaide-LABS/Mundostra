'use client';

import { useEffect, useRef } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useChat } from '@/context/ChatContext';
import { ChatMessageBubble, TypingIndicator } from './ChatMessageBubble';
import { ChatInput } from './ChatInput';
import { SuggestedChips } from './SuggestedChips';
import { ResolutionCard } from './ResolutionCard';

export function ChatContainer() {
  const { state, sendMessage, reset } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [state.messages, state.isProcessing]);

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-gray-200 bg-white px-4 py-3 shadow-sm">
        <div className="flex items-center gap-3">
          <Image
            src="/logo.png"
            alt="Mundostra"
            width={32}
            height={32}
            className="rounded-lg"
          />
          <div>
            <h1 className="text-sm font-bold tracking-wide text-gray-900">MUNDOSTRA</h1>
            <p className="text-[10px] uppercase tracking-widest text-gray-400">
              Travel Assistant
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/admin"
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-500 transition-colors hover:bg-gray-50 hover:text-gray-700"
          >
            Admin
          </Link>
          <button
            onClick={reset}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-500 transition-colors hover:bg-gray-50 hover:text-gray-700"
          >
            New Chat
          </button>
        </div>
      </header>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {state.messages.map((msg) => (
          <div key={msg.id}>
            <ChatMessageBubble message={msg} />
            {msg.showOptions && msg.resolution && msg.resolution.status === 'proposed' && (
              <div className="mt-2">
                <ResolutionCard
                  resolution={msg.resolution}
                  onConfirm={() => sendMessage('Yes, book it')}
                  onOptions={() => sendMessage('Show me other options')}
                />
              </div>
            )}
          </div>
        ))}

        {state.isProcessing && <TypingIndicator />}
      </div>

      {/* Chips */}
      {state.showChips && (
        <div className="pb-2">
          <SuggestedChips onSelect={sendMessage} />
        </div>
      )}

      {/* Input */}
      <ChatInput onSend={sendMessage} disabled={state.isProcessing} />
    </div>
  );
}
