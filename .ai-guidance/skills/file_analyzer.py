"""
ファイル分析スキル

プロジェクト内のソースコードを分析し、品質メトリクスとレポートを生成
"""

import re
import ast
from typing import Dict, Any, List
from pathlib import Path
from collections import defaultdict

from .base import Skill


class FileAnalyzerSkill(Skill):
    """ファイル分析スキル

    機能:
    - ソースコード品質分析
    - 複雑度計算
    - 課題検出
    - ファイル構造分析
    - 言語別統計
    """

    def __init__(self, config: Dict[str, Any] = None):
        default_config = {
            "name": "file_analyzer",
            "version": "1.0.0",
            "description": "ソースコードファイルの品質分析を実行",
            "triggers": [
                "ファイル分析",
                "コード分析",
                "ソース解析",
                "品質チェック",
                "メトリクス",
                "複雑度",
            ],
            "required_tools": ["view", "glob"],
            "timeout": 600,
        }

        if config:
            default_config.update(config)

        super().__init__(default_config)

        # 分析設定
        self.max_line_length = self.config.get("max_line_length", 100)
        self.max_function_lines = self.config.get("max_function_lines", 50)
        self.max_complexity = self.config.get("max_complexity", 10)

        # サポート言語
        self.supported_extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "React",
            ".tsx": "React TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".rb": "Ruby",
            ".php": "PHP",
            ".cpp": "C++",
            ".c": "C",
            ".cs": "C#",
            ".swift": "Swift",
            ".kt": "Kotlin",
        }

        # 除外パターン
        self.exclude_patterns = [
            "*/node_modules/*",
            "*/venv/*",
            "*/env/*",
            "*/.git/*",
            "*/dist/*",
            "*/build/*",
            "*/__pycache__/*",
            "*.min.js",
            "*.bundle.js",
        ]

    async def execute(
        self,
        file_paths: List[str] = None,
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """ファイル分析実行"""

        try:
            # ファイル検索
            if not file_paths:
                file_paths = await self._discover_files(
                    include_patterns, exclude_patterns
                )

            self.add_debug_info(f"分析対象ファイル: {len(file_paths)}個")

            # 分析実行
            analysis_results = []
            language_stats = defaultdict(int)
            total_metrics = {
                "total_files": 0,
                "total_lines": 0,
                "total_size_bytes": 0,
                "issues_count": 0,
                "high_complexity_files": 0,
            }

            for file_path in file_paths:
                try:
                    analysis = await self._analyze_single_file(file_path)
                    if analysis:
                        analysis_results.append(analysis)

                        # 統計更新
                        language = analysis["language"]
                        language_stats[language] += 1
                        total_metrics["total_files"] += 1
                        total_metrics["total_lines"] += analysis["metrics"][
                            "lines_count"
                        ]
                        total_metrics["total_size_bytes"] += analysis["metrics"][
                            "size_bytes"
                        ]
                        total_metrics["issues_count"] += len(analysis["issues"])

                        if (
                            analysis["metrics"]["complexity_score"]
                            > self.max_complexity
                        ):
                            total_metrics["high_complexity_files"] += 1

                        self.add_result(f"分析完了: {file_path}")

                except Exception as e:
                    self.add_warning(f"ファイル分析スキップ {file_path}: {e}")

            # 分析レポート生成
            report = self._generate_analysis_report(
                analysis_results, dict(language_stats), total_metrics
            )

            return {
                "success": True,
                "analyzed_files": len(analysis_results),
                "skipped_files": len(file_paths) - len(analysis_results),
                "file_analyses": analysis_results,
                "language_statistics": dict(language_stats),
                "total_metrics": total_metrics,
                "analysis_report": report,
                "summary": self._generate_summary(analysis_results, total_metrics),
            }

        except Exception as e:
            self.add_error(f"ファイル分析実行エラー: {e}")
            return {
                "success": False,
                "error": str(e),
                "partial_results": getattr(self, "_partial_results", []),
            }

    async def _discover_files(
        self, include_patterns: List[str] = None, exclude_patterns: List[str] = None
    ) -> List[str]:
        """分析対象ファイルを自動検索"""

        all_files = []

        # 対象拡張子でファイル検索
        search_patterns = include_patterns or [
            f"**/*{ext}" for ext in self.supported_extensions.keys()
        ]

        for pattern in search_patterns:
            try:
                files = await self.call_tool("glob", pattern=pattern)
                if isinstance(files, list):
                    all_files.extend(files)
            except Exception as e:
                self.add_warning(f"ファイル検索エラー {pattern}: {e}")

        # 除外フィルタ適用
        exclude_list = exclude_patterns or self.exclude_patterns
        filtered_files = []

        for file_path in all_files:
            if not any(
                self._matches_pattern(file_path, pattern) for pattern in exclude_list
            ):
                filtered_files.append(file_path)

        return filtered_files

    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """ファイルパスがパターンにマッチするかチェック"""
        # 簡易的なグロブパターンマッチング
        pattern = pattern.replace("*", ".*").replace("?", ".")
        return re.search(pattern, file_path) is not None

    async def _analyze_single_file(self, file_path: str) -> Dict[str, Any]:
        """単一ファイルの分析"""

        try:
            # ファイル内容取得
            content = await self.call_tool("view", path=file_path)
            if not content or not isinstance(content, str):
                return None

            # 基本情報
            path_obj = Path(file_path)
            language = self.supported_extensions.get(path_obj.suffix, "Unknown")

            # メトリクス計算
            metrics = self._calculate_metrics(content, language)

            # 課題検出
            issues = self._detect_issues(content, language, file_path)

            # 構造分析
            structure = await self._analyze_structure(content, language)

            return {
                "file_path": file_path,
                "language": language,
                "extension": path_obj.suffix,
                "metrics": metrics,
                "issues": issues,
                "structure": structure,
                "analysis_timestamp": self.start_time,
            }

        except Exception as e:
            self.add_debug_info(f"ファイル分析エラー {file_path}: {e}")
            return None

    def _calculate_metrics(self, content: str, language: str) -> Dict[str, Any]:
        """ファイルメトリクス計算"""

        lines = content.splitlines()

        # 基本メトリクス
        metrics = {
            "lines_count": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "comment_lines": self._count_comment_lines(lines, language),
            "size_bytes": len(content.encode("utf-8")),
            "character_count": len(content),
            "word_count": len(content.split()),
            "max_line_length": max(len(line) for line in lines) if lines else 0,
            "average_line_length": (
                sum(len(line) for line in lines) / len(lines) if lines else 0
            ),
        }

        # 複雑度計算
        metrics["complexity_score"] = self._calculate_complexity(content, language)

        # コード品質指標
        metrics["code_density"] = (
            (metrics["non_empty_lines"] - metrics["comment_lines"])
            / metrics["lines_count"]
            if metrics["lines_count"] > 0
            else 0
        )

        metrics["comment_ratio"] = (
            metrics["comment_lines"] / metrics["lines_count"]
            if metrics["lines_count"] > 0
            else 0
        )

        return metrics

    def _count_comment_lines(self, lines: List[str], language: str) -> int:
        """コメント行数をカウント"""

        comment_count = 0

        # 言語別コメントパターン
        comment_patterns = {
            "Python": [r"^\s*#"],
            "JavaScript": [r"^\s*//", r"^\s*/\*", r"^\s*\*"],
            "TypeScript": [r"^\s*//", r"^\s*/\*", r"^\s*\*"],
            "Java": [r"^\s*//", r"^\s*/\*", r"^\s*\*"],
            "C++": [r"^\s*//", r"^\s*/\*", r"^\s*\*"],
            "C": [r"^\s*/\*", r"^\s*\*"],
            "Go": [r"^\s*//"],
            "Ruby": [r"^\s*#"],
            "PHP": [r"^\s*//", r"^\s*#", r"^\s*/\*"],
        }

        patterns = comment_patterns.get(language, [r"^\s*//"])

        for line in lines:
            if any(re.match(pattern, line) for pattern in patterns):
                comment_count += 1

        return comment_count

    def _calculate_complexity(self, content: str, language: str) -> int:
        """循環的複雑度の概算計算"""

        complexity = 1  # ベースライン

        # 制御フロー文のカウント
        control_keywords = {
            "Python": [
                "if",
                "elif",
                "for",
                "while",
                "try",
                "except",
                "with",
                "and",
                "or",
            ],
            "JavaScript": [
                "if",
                "for",
                "while",
                "try",
                "catch",
                "switch",
                "case",
                "&&",
                "||",
            ],
            "TypeScript": [
                "if",
                "for",
                "while",
                "try",
                "catch",
                "switch",
                "case",
                "&&",
                "||",
            ],
            "Java": [
                "if",
                "for",
                "while",
                "try",
                "catch",
                "switch",
                "case",
                "&&",
                "||",
            ],
            "Go": ["if", "for", "switch", "case", "select", "&&", "||"],
            "default": ["if", "for", "while", "try", "catch", "&&", "||"],
        }

        keywords = control_keywords.get(language, control_keywords["default"])

        # 単語境界を考慮した検索
        for keyword in keywords:
            # 演算子の場合
            if keyword in ["&&", "||", "and", "or"]:
                complexity += content.count(keyword)
            else:
                # キーワードの場合、単語境界を確認
                pattern = rf"\b{re.escape(keyword)}\b"
                complexity += len(re.findall(pattern, content))

        return complexity

    def _detect_issues(
        self, content: str, language: str, file_path: str
    ) -> List[Dict[str, Any]]:
        """コード課題の検出"""

        issues = []
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            # 長すぎる行
            if len(line) > self.max_line_length:
                issues.append(
                    {
                        "type": "long_line",
                        "severity": "warning",
                        "line": i,
                        "message": f"行が長すぎます ({len(line)} 文字, 推奨: {self.max_line_length})",
                        "suggestion": "行を分割することを検討してください",
                    }
                )

            # タブとスペースの混在
            if "\t" in line and "    " in line:
                issues.append(
                    {
                        "type": "mixed_indentation",
                        "severity": "error",
                        "line": i,
                        "message": "タブとスペースが混在しています",
                        "suggestion": "統一されたインデントスタイルを使用してください",
                    }
                )

            # 末尾の空白
            if line.rstrip() != line:
                issues.append(
                    {
                        "type": "trailing_whitespace",
                        "severity": "warning",
                        "line": i,
                        "message": "行末に不要な空白があります",
                        "suggestion": "末尾空白を削除してください",
                    }
                )

            # TODOコメント
            if re.search(r"\b(TODO|FIXME|HACK|XXX)\b", line, re.IGNORECASE):
                issues.append(
                    {
                        "type": "todo_comment",
                        "severity": "info",
                        "line": i,
                        "message": "TODOコメントが残っています",
                        "suggestion": "課題を解決するか、issueとして管理してください",
                    }
                )

            # ハードコードされた値
            if (
                language in ["Python", "JavaScript", "TypeScript"]
                and "import" not in line
            ):
                magic_numbers = re.findall(r"\b\d{2,}\b", line)
                if magic_numbers and not any(
                    num in ["100", "200", "404", "500"] for num in magic_numbers
                ):
                    issues.append(
                        {
                            "type": "magic_number",
                            "severity": "warning",
                            "line": i,
                            "message": f'マジックナンバーの可能性: {", ".join(magic_numbers)}',
                            "suggestion": "定数として定義することを検討してください",
                        }
                    )

        # 言語固有の課題検出
        issues.extend(self._detect_language_specific_issues(content, language))

        return issues

    def _detect_language_specific_issues(
        self, content: str, language: str
    ) -> List[Dict[str, Any]]:
        """言語固有の課題検出"""

        issues = []

        if language == "Python":
            issues.extend(self._detect_python_issues(content))
        elif language in ["JavaScript", "TypeScript"]:
            issues.extend(self._detect_javascript_issues(content))

        return issues

    def _detect_python_issues(self, content: str) -> List[Dict[str, Any]]:
        """Python固有の課題検出"""

        issues = []

        try:
            # AST解析
            tree = ast.parse(content)

            # 関数の複雑度チェック
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno + 1
                    if func_lines > self.max_function_lines:
                        issues.append(
                            {
                                "type": "long_function",
                                "severity": "warning",
                                "line": node.lineno,
                                "message": f"関数が長すぎます ({func_lines} 行, 推奨: {self.max_function_lines})",
                                "suggestion": "関数を分割することを検討してください",
                                "function_name": node.name,
                            }
                        )

        except SyntaxError as e:
            issues.append(
                {
                    "type": "syntax_error",
                    "severity": "error",
                    "line": e.lineno or 1,
                    "message": f"構文エラー: {e.msg}",
                    "suggestion": "構文を修正してください",
                }
            )

        return issues

    def _detect_javascript_issues(self, content: str) -> List[Dict[str, Any]]:
        """JavaScript/TypeScript固有の課題検出"""

        issues = []

        # console.log の検出
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            if "console.log" in line and not line.strip().startswith("//"):
                issues.append(
                    {
                        "type": "console_log",
                        "severity": "info",
                        "line": i,
                        "message": "console.log文が残っています",
                        "suggestion": "本番環境では削除してください",
                    }
                )

        return issues

    async def _analyze_structure(self, content: str, language: str) -> Dict[str, Any]:
        """ファイル構造分析"""

        structure = {
            "functions_count": 0,
            "classes_count": 0,
            "imports_count": 0,
            "exports_count": 0,
        }

        if language == "Python":
            structure.update(self._analyze_python_structure(content))
        elif language in ["JavaScript", "TypeScript"]:
            structure.update(self._analyze_javascript_structure(content))

        return structure

    def _analyze_python_structure(self, content: str) -> Dict[str, Any]:
        """Python構造分析"""

        structure = {}

        try:
            tree = ast.parse(content)

            functions = [
                node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
            ]
            classes = [
                node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
            ]
            imports = [
                node
                for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom))
            ]

            structure.update(
                {
                    "functions_count": len(functions),
                    "classes_count": len(classes),
                    "imports_count": len(imports),
                    "function_names": [f.name for f in functions],
                    "class_names": [c.name for c in classes],
                }
            )

        except SyntaxError:
            pass

        return structure

    def _analyze_javascript_structure(self, content: str) -> Dict[str, Any]:
        """JavaScript/TypeScript構造分析"""

        # 正規表現ベースの簡易分析
        structure = {}

        # 関数検出
        function_patterns = [
            r"function\s+(\w+)",
            r"const\s+(\w+)\s*=\s*\(",
            r"let\s+(\w+)\s*=\s*\(",
            r"var\s+(\w+)\s*=\s*\(",
            r"(\w+)\s*:\s*function",
            r"(\w+)\s*=>\s*",
        ]

        functions = []
        for pattern in function_patterns:
            functions.extend(re.findall(pattern, content))

        # クラス検出
        classes = re.findall(r"class\s+(\w+)", content)

        # import/export検出
        imports = len(re.findall(r"import\s+", content))
        exports = len(re.findall(r"export\s+", content))

        structure.update(
            {
                "functions_count": len(functions),
                "classes_count": len(classes),
                "imports_count": imports,
                "exports_count": exports,
                "function_names": functions,
                "class_names": classes,
            }
        )

        return structure

    def _generate_analysis_report(
        self,
        analysis_results: List[Dict[str, Any]],
        language_stats: Dict[str, int],
        total_metrics: Dict[str, Any],
    ) -> str:
        """分析レポート生成"""

        report = "# ファイル分析レポート\n\n"

        # サマリー
        report += "## サマリー\n\n"
        report += f"- **分析ファイル数**: {total_metrics['total_files']}\n"
        report += f"- **総行数**: {total_metrics['total_lines']:,}\n"
        report += f"- **総サイズ**: {total_metrics['total_size_bytes']:,} バイト\n"
        report += f"- **検出課題数**: {total_metrics['issues_count']}\n"
        report += (
            f"- **高複雑度ファイル**: {total_metrics['high_complexity_files']}\n\n"
        )

        # 言語統計
        report += "## 言語別統計\n\n"
        for language, count in sorted(
            language_stats.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (count / total_metrics["total_files"]) * 100
            report += f"- **{language}**: {count} ファイル ({percentage:.1f}%)\n"
        report += "\n"

        # 品質指標
        if analysis_results:
            avg_complexity = sum(
                r["metrics"]["complexity_score"] for r in analysis_results
            ) / len(analysis_results)
            avg_line_length = sum(
                r["metrics"]["average_line_length"] for r in analysis_results
            ) / len(analysis_results)

            report += "## 品質指標\n\n"
            report += f"- **平均複雑度**: {avg_complexity:.1f}\n"
            report += f"- **平均行長**: {avg_line_length:.1f} 文字\n\n"

        # 高課題ファイル
        high_issue_files = [r for r in analysis_results if len(r["issues"]) > 5]

        if high_issue_files:
            report += "## 高課題ファイル\n\n"
            for file_analysis in sorted(
                high_issue_files, key=lambda x: len(x["issues"]), reverse=True
            )[:10]:
                report += f"- **{file_analysis['file_path']}**: {len(file_analysis['issues'])} 課題\n"
            report += "\n"

        return report

    def _generate_summary(
        self, analysis_results: List[Dict[str, Any]], total_metrics: Dict[str, Any]
    ) -> str:
        """サマリー生成"""

        if not analysis_results:
            return "ファイル分析が完了しましたが、分析対象ファイルがありませんでした。"

        avg_issues = total_metrics["issues_count"] / len(analysis_results)

        summary = f"{len(analysis_results)}個のファイルを分析しました。"
        summary += f"総行数: {total_metrics['total_lines']:,}行、"
        summary += f"平均課題数: {avg_issues:.1f}個/ファイル。"

        if total_metrics["high_complexity_files"] > 0:
            summary += f"高複雑度ファイルが{total_metrics['high_complexity_files']}個検出されました。"

        return summary
