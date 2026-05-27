const API_URL = 'https://api.openai.com/v1/chat/completions';

export const generateReportSummary = async (
  rangeLabel: string,
  startDate: string,
  endDate: string,
  projectName: string,
  items: string[]
): Promise<string> => {
  const apiKey = import.meta.env.VITE_OPENAI_API_KEY as string;
  if (!apiKey) throw new Error('OpenAI API 키가 설정되지 않았습니다.');
  if (items.length === 0) throw new Error('요약할 업무 항목이 없습니다.');

  const itemList = items.map((it) => `- ${it}`).join('\n');
  const userPrompt =
    `다음은 "${projectName}" 프로젝트의 ${rangeLabel} 업무 내용(${startDate} ~ ${endDate})입니다.\n\n` +
    `${itemList}\n\n` +
    `위 내용을 아래 조건에 맞게 요약해 주세요.\n` +
    `1. 불릿 포인트(•) 형식으로 작성\n` +
    `2. 각 항목은 한 문장으로 핵심만 서술\n` +
    `3. 마크다운 기호(**)는 사용하지 않음\n` +
    `4. 한국어로 작성`;

  const res = await fetch(API_URL, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [
        {
          role: 'system',
          content:
            '당신은 기업 업무 보고서 작성 전문가입니다. ' +
            '주어진 업무 일지 항목을 간결하고 전문적인 한국어 보고서 형식으로 요약합니다.',
        },
        { role: 'user', content: userPrompt },
      ],
      max_tokens: 800,
      temperature: 0.3,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { error?: { message?: string } };
    throw new Error(err?.error?.message ?? `OpenAI API 오류 (${res.status})`);
  }

  const data = await res.json() as { choices?: { message?: { content?: string } }[] };
  const text = data.choices?.[0]?.message?.content?.trim() ?? '';
  if (!text) throw new Error('OpenAI 응답이 비어 있습니다.');
  return text;
};
