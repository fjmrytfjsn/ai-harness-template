# code_review.py
"""
セキュリティ、パフォーマンス、スタイル分析を含む高度なコードレビュースキル。
"""

from ai_guidance import skill, Skill
import ast
import re
from pathlib import Path

@skill(
    name="code_review",
    description="セキュリティと品質分析を含む包括的コードレビュー",
    triggers=["レビュー", "コード分析", "品質チェック", "コードレビュー"],
    dependencies=["filesystem", "git"],
    confidence_threshold=0.8
)
class CodeReviewSkill(Skill):
    """高度なコードレビュースキル"""

    def __init__(self):
        super().__init__()
        self.security_patterns = self._load_security_patterns()
        self.performance_checks = self._load_performance_checks()

    async def execute(self, files=None, focus="全て", severity="medium"):
        """包括的コードレビューの実行"""

        if not files:
            files = await self.detect_changed_files()

        if isinstance(files, str):
            files = [files]

        review_results = {
            "summary": {"total_files": len(files), "total_issues": 0},
            "files": []
        }

        for file_path in files:
            file_result = await self.review_file(file_path, focus, severity)
            review_results["files"].append(file_result)
            review_results["summary"]["total_issues"] += len(file_result["issues"])

        review_results["recommendations"] = self.generate_recommendations(review_results)

        return review_results

    async def review_file(self, file_path, focus, severity):
        """個別ファイルのレビュー"""

        try:
            content = await self.read_file(file_path)
            file_ext = Path(file_path).suffix

            issues = []

            # セキュリティ分析
            if focus in ["全て", "セキュリティ"]:
                security_issues = self.check_security(content, file_ext)
                issues.extend(security_issues)

            # パフォーマンス分析
            if focus in ["全て", "パフォーマンス"]:
                perf_issues = self.check_performance(content, file_ext)
                issues.extend(perf_issues)

            # コードスタイル
            if focus in ["全て", "スタイル"]:
                style_issues = self.check_style(content, file_ext)
                issues.extend(style_issues)

            # バグ検出
            if focus in ["全て", "バグ"]:
                bug_issues = self.check_bugs(content, file_ext)
                issues.extend(bug_issues)

            # 重要度でフィルタリング
            filtered_issues = [
                issue for issue in issues
                if self.meets_severity_threshold(issue["severity"], severity)
            ]

            return {
                "file": file_path,
                "language": self.detect_language(file_ext),
                "lines": len(content.splitlines()),
                "issues": filtered_issues,
                "complexity_score": self.calculate_complexity(content, file_ext)
            }

        except Exception as e:
            return {
                "file": file_path,
                "error": str(e),
                "issues": []
            }

    def check_security(self, content, file_ext):
        """セキュリティ脆弱性のチェック"""
        issues = []

        # 一般的なセキュリティパターン
        patterns = {
            "hardcoded_secrets": r"(password|secret|key|token)\s*=\s*[\"'][^\"']+[\"']",
            "sql_injection": r"(SELECT|INSERT|UPDATE|DELETE).*\+.*\+",
            "xss_risk": r"innerHTML\s*=",
            "command_injection": r"(os\.system|subprocess\.call|exec\()",
            "unsafe_deserialization": r"(pickle\.loads|yaml\.load\()"
        }

        for pattern_name, pattern in patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    "type": "セキュリティ",
                    "category": pattern_name,
                    "line": line_num,
                    "severity": "高" if pattern_name in ["hardcoded_secrets", "sql_injection"] else "中",
                    "message": f"潜在的セキュリティ問題: {pattern_name.replace('_', ' ')}",
                    "code": match.group(0)
                })

        return issues

    def check_performance(self, content, file_ext):
        """パフォーマンス問題のチェック"""
        issues = []

        if file_ext == '.py':
            # Python固有のパフォーマンスチェック
            patterns = {
                "nested_loops": r"for\s+\w+.*:\s*\n\s*for\s+\w+.*:",
                "inefficient_string_concat": r"\+\=\s*[\"'][^\"']*[\"']",
                "global_imports_in_function": r"def\s+\w+.*:\s*\n\s*import\s+",
                "list_comprehension_opportunity": r"for\s+\w+\s+in.*:\s*\n\s*\w+\.append\("
            }

            for pattern_name, pattern in patterns.items():
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        "type": "パフォーマンス",
                        "category": pattern_name,
                        "line": line_num,
                        "severity": "中",
                        "message": f"パフォーマンス懸念: {pattern_name.replace('_', ' ')}",
                        "suggestion": self.get_performance_suggestion(pattern_name)
                    })

        return issues

    def check_style(self, content, file_ext):
        """コードスタイルとフォーマットのチェック"""
        issues = []

        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            # 長い行
            if len(line) > 120:
                issues.append({
                    "type": "スタイル",
                    "category": "行の長さ",
                    "line": i,
                    "severity": "低",
                    "message": f"行が長すぎます（{len(line)}文字）"
                })

            # 行末空白
            if line.endswith(' ') or line.endswith('\t'):
                issues.append({
                    "type": "スタイル",
                    "category": "行末空白",
                    "line": i,
                    "severity": "低",
                    "message": "行末に空白があります"
                })

            # 混合インデント（Pythonの場合）
            if file_ext == '.py' and line.strip() and ('\t' in line and '    ' in line):
                issues.append({
                    "type": "スタイル",
                    "category": "混合インデント",
                    "line": i,
                    "severity": "中",
                    "message": "タブとスペースが混在しています"
                })

        return issues

    def check_bugs(self, content, file_ext):
        """一般的なバグパターンのチェック"""
        issues = []

        # 一般的なバグパターン
        patterns = {
            "empty_except": r"except.*:\s*\n\s*pass",
            "bare_except": r"except:\s*\n",
            "mutable_default_arg": r"def\s+\w+.*=\s*\[\]",
            "comparison_with_none": r"==\s*None|!=\s*None"
        }

        for pattern_name, pattern in patterns.items():
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    "type": "バグリスク",
                    "category": pattern_name,
                    "line": line_num,
                    "severity": "中",
                    "message": f"潜在的バグ: {pattern_name.replace('_', ' ')}",
                    "suggestion": self.get_bug_suggestion(pattern_name)
                })

        return issues

    def calculate_complexity(self, content, file_ext):
        """循環的複雑度スコアの計算"""
        if file_ext != '.py':
            return None

        try:
            tree = ast.parse(content)
            complexity = 0

            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                    complexity += 1
                elif isinstance(node, ast.FunctionDef):
                    complexity += 1

            return min(complexity, 100)  # 100でキャップ

        except SyntaxError:
            return None

    def generate_recommendations(self, review_results):
        """高レベル推奨事項の生成"""

        total_issues = review_results["summary"]["total_issues"]

        if total_issues == 0:
            return ["コードは良好です！大きな問題は検出されませんでした。"]

        recommendations = []

        # タイプ別問題数をカウント
        issue_types = {}
        for file_result in review_results["files"]:
            for issue in file_result["issues"]:
                issue_type = issue["type"]
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

        # ターゲット推奨事項を生成
        if issue_types.get("セキュリティ", 0) > 0:
            recommendations.append("🔒 デプロイ前にセキュリティ脆弱性に対処してください")

        if issue_types.get("パフォーマンス", 0) > 3:
            recommendations.append("⚡ 効率向上のためパフォーマンス最適化を検討してください")

        if issue_types.get("バグリスク", 0) > 0:
            recommendations.append("🐛 ランタイム問題を防ぐため潜在的バグパターンをレビューしてください")

        if issue_types.get("スタイル", 0) > 10:
            recommendations.append("🎨 自動コードフォーマッターの実行を検討してください")

        return recommendations

    def _load_security_patterns(self):
        """セキュリティ分析パターンの読み込み"""
        return {
            "sql_injection": "潜在的SQLインジェクション脆弱性",
            "xss_risk": "クロスサイトスクリプティング（XSS）リスク",
            "hardcoded_secrets": "ハードコードされた認証情報を検出"
        }

    def _load_performance_checks(self):
        """パフォーマンスチェック定義の読み込み"""
        return {
            "nested_loops": "ネストしたループのアルゴリズム最適化を検討",
            "inefficient_string_concat": "複数の文字列連結にはjoin()を使用"
        }

    def get_performance_suggestion(self, pattern_name):
        """パフォーマンス改善提案の取得"""
        suggestions = {
            "nested_loops": "リスト内包表記を使用するかアルゴリズム複雑度の最適化を検討",
            "inefficient_string_concat": "文字列連結には+=の代わりに''.join()を使用",
            "list_comprehension_opportunity": "より良いパフォーマンスのためリスト内包表記を検討"
        }
        return suggestions.get(pattern_name, "このパターンの最適化を検討してください")

    def get_bug_suggestion(self, pattern_name):
        """バグ修正提案の取得"""
        suggestions = {
            "empty_except": "具体的な例外処理またはログを追加",
            "bare_except": "キャッチする例外タイプを指定",
            "mutable_default_arg": "デフォルトにNoneを使用し、関数本体でミュータブルオブジェクトを作成",
            "comparison_with_none": "==や!=の代わりに'is None'または'is not None'を使用"
        }
        return suggestions.get(pattern_name, "潜在的問題についてこのパターンをレビュー")

    def meets_severity_threshold(self, issue_severity, min_severity):
        """問題が重要度閾値を満たすかチェック"""
        severity_levels = {"低": 1, "中": 2, "高": 3}
        return severity_levels.get(issue_severity, 0) >= severity_levels.get(min_severity, 1)

    def detect_language(self, file_ext):
        """ファイル拡張子からプログラミング言語を検出"""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust'
        }
        return language_map.get(file_ext, '不明')
