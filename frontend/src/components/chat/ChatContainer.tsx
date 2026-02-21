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
  const { state, sendMessage, sendImage, reset } = useChat();
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

      {/* Persistent ticket download bar */}
      {state.ticketPdfUrl && (
        <div className="flex items-center justify-between border-t border-purple-200 bg-purple-50 px-4 py-2.5">
          <div className="flex items-center gap-2 text-sm text-purple-700">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            <span className="font-medium">Your ticket is ready</span>
          </div>
          <a
            href={`${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}${state.ticketPdfUrl}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 rounded-full bg-purple-600 px-4 py-1.5 text-xs font-medium text-white transition-colors hover:bg-purple-700"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Download PDF
          </a>
        </div>
      )}

      {/* Input */}
      <ChatInput onSend={sendMessage} onSendImage={sendImage} disabled={state.isProcessing} />
    </div>
  );
}
