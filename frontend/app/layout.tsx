import React from 'react';

export const metadata = {
  title: 'Chat With Your Docs',
  description: 'Upload docs and chat with them',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: 'Arial, sans-serif', background: '#f5f7fb' }}>
        {children}
      </body>
    </html>
  );
}
