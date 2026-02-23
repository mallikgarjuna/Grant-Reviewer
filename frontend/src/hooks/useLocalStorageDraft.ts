"use client";

import { useEffect, useState } from "react";

function loadStoredValue<T>(storageKey: string, initialValue: T): T {
  if (!storageKey || typeof window === "undefined") {
    return initialValue;
  }

  const raw = window.localStorage.getItem(storageKey);
  if (!raw) {
    return initialValue;
  }

  try {
    return JSON.parse(raw) as T;
  } catch {
    return initialValue;
  }
}

export function useLocalStorageDraft<T>(storageKey: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => loadStoredValue(storageKey, initialValue));

  useEffect(() => {
    if (!storageKey) {
      return;
    }
    window.localStorage.setItem(storageKey, JSON.stringify(value));
  }, [storageKey, value]);

  const clear = () => {
    if (!storageKey) {
      return;
    }
    window.localStorage.removeItem(storageKey);
    setValue(initialValue);
  };

  return { value, setValue, clear };
}
