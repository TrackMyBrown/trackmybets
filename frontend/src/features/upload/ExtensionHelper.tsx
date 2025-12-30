type ExtensionHelperProps = {
  stepLabel: string;
};

function ExtensionHelper({ stepLabel }: ExtensionHelperProps) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
      <div className="flex flex-col gap-2">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">{stepLabel}</p>
        <h3 className="text-2xl font-semibold text-slate-900">Install the TrackMyBets helper extension (optional)</h3>
        <p className="text-sm text-slate-600">
          Sportsbet only lets you download the most 50 recent transactions via their default “Download Spreadsheet”
          button. Install our extension to pull full histories before you upload the CSV here.
        </p>
      </div>

      <div className="mt-6 space-y-3 text-sm text-slate-600">
        <p className="font-semibold text-slate-900">How to use it</p>
        <ol className="list-decimal space-y-1 pl-5">
          <li>
            <a
              href="/trackmybets-helper-extension.zip"
              download
              className="font-semibold text-brand-600 underline"
            >
              Download the TrackMyBets helper extension (.zip)
            </a>{" "}
            and unzip it somewhere safe.
          </li>
          <li>
            Open <code>chrome://extensions</code>, enable Developer Mode, and click <strong>Load unpacked</strong> to
            select the unzipped folder (it contains <code>manifest.json</code>).
          </li>
          <li>Log in to sportsbet.com.au, choose your date range, and click the TrackMyBets extension icon.</li>
          <li>The extension downloads a <code>.csv</code> with every bet in that range. Upload it here.</li>
        </ol>
      </div>

      <div className="mt-4 rounded-2xl bg-slate-50 p-4 text-xs text-slate-600">
        <p className="font-semibold text-slate-800">Privacy guardrails</p>
        <ul className="list-disc space-y-1 pl-5">
          <li>No data leaves your browser. The extension only calls Sportsbet and saves a file locally.</li>
          <li>Source is bundled with this project, so you can inspect or modify it.</li>
          <li>Remove the extension any time; TrackMyBets never stores your session tokens.</li>
        </ul>
      </div>
    </section>
  );
}

export default ExtensionHelper;
