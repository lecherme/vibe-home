# F14 Acceptance Criteria

## Build (T01)

| ID | Criterion |
|----|-----------|
| A1 | PaginationControls: Previous Button 使用 shadcn Button，保留 slate outline className |
| A2 | PaginationControls: Next Button 使用 shadcn Button，保留 slate outline className |
| A3 | PaginationControls: Go Button 使用 shadcn Button，保留 slate outline className |
| A4 | PaginationControls: pageInput Input 使用 shadcn Input，保留原有 className |
| A5 | PaginationControls: sr-only Label 使用 shadcn Label |
| A6 | PaginationControls: 全部逻辑保留（pageInput、useEffect、clampPage、goToPage、handleSubmit、handleKeyDown） |
| A7 | NavBar: Sign out Button 使用 shadcn Button，保留 ghost/slate className |
| A8 | NavBar: handleSignOut 逻辑完整（signOut + router.refresh + router.push） |
| A9 | tsc --noEmit exit 0 |

## Manual (T03 Claude)

| ID | Criterion |
|----|-----------|
| A10 | 分页 Previous 按钮正常，page > 1 时可点 |
| A11 | 分页 Next 按钮正常，page < totalPages 时可点 |
| A12 | Go 输入页码 → Enter 或点 Go → 正确跳页，超范围 clamp |
| A13 | NavBar Sign out → 跳 /login |
| A14 | 视觉与迁移前一致（slate 色调，无 indigo 入侵） |
