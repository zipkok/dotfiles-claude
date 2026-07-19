export const meta = {
  name: 'doc-review-panel',
  description: '영어 문서를 6개 디멘션으로 병렬 리뷰 후 하나의 리포트로 수렴',
  phases: [
    { title: 'Review', detail: 'structure/grammar/readability/reproducibility/terminology/audience-tone 6개 디멘션 병렬 체크' },
    { title: 'Synthesize', detail: '디멘션별 결과를 하나의 리포트로 수렴' },
  ],
}

// args: { docPath, context? }
// 한 번 호출 = 문서 1개에 대한 리뷰 1회.
// Workflow 툴 호출 경로에 따라 args가 JSON 문자열로 넘어오는 경우가 있어 방어적으로 파싱한다.

const input = typeof args === 'string' ? JSON.parse(args) : args

if (!input || !input.docPath) {
  throw new Error('args.docPath가 필요합니다')
}

phase('Review')
const dimensions = ['structure', 'grammar', 'readability', 'reproducibility', 'terminology', 'audience-tone']
log(`Review: ${dimensions.join(', ')} 6개 디멘션 병렬 체크`)
const findings = await parallel(
  dimensions.map(d => () =>
    agent(
      `디멘션: ${d}\n문서 경로: ${input.docPath}\n맥락: ${input.context || ''}`,
      { agentType: 'doc-review-checker', label: `review:${d}`, phase: 'Review' }
    )
  )
)

phase('Synthesize')
const report = await agent(
  `문서 경로: ${input.docPath}\n디멘션별 결과: ${JSON.stringify(findings.filter(Boolean))}`,
  { agentType: 'doc-review-synthesizer', label: 'synthesize', phase: 'Synthesize' }
)

return { docPath: input.docPath, findings: findings.filter(Boolean), report }
