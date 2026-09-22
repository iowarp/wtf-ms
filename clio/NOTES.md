# Clio port validation and provenance

All implementation writes are confined to /home/akougkas/iowarp/wtf-ms/clio/.
No extension was installed, no configure command was run, no git add/commit/tag/
checkout was run, and /home/akougkas/iowarp/clio-coder was not modified.

The canonical README and all 17 command and 5 agent files were read before the
port. The earlier scratchpad skeleton supplied validated Clio mechanics only;
its old git-init/automatic-recording policy and incomplete command set were not
carried forward. The skill-creator guidance was applied to the six bound skills.

## Content adaptation

Every canonical interview question, choice set, decision gate, completion branch
and next-step block is retained in Clio terms. URL requests extend the literature
scope question; provided URLs replace unavailable general WebSearch behavior.
All agent returns use mutation-report JSON with status-prefixed summary strings.
Missing facts and decisions use the two needs_input checkpoint prefixes. Fresh
re-dispatches carry all prior context and answers; files are read back after writes.

The executor was ported from the restored canonical task-executor.md file.

The task verifier is additional Clio support, uses read-only capability and an
empty mutation set, and returns typed checks through mutation-report. It does
not upgrade advisory findings into automatic scientific rejection. The default
fleet omits the optional physics code step to preserve the researcher decision
gate; README documents a valid command registry example for separate project use.

Copied references intentionally retain their original terminology, including a
WebSearch label in traditional-workflows.md. They are verbatim domain reference
content, not declarations of available Clio tools; persona/skill instructions
specify provided-URL fetching only. No script or reference content was rewritten.

## Validation boundaries

Before running discover, inspected clio-coder src/cli/extensions.ts:154 and
src/domains/extensions/discovery.ts:376: discovery reads, parses, validates and
prints candidates; it does not call installation or registration. The command
validates manifest/resources/compatibility, not every resource's internal schema.
Production loaders therefore also check all six recipe policies and bound skills,
all 17 mixed-case prompt names and extensionRoot references, and the v4 fleet.
No model, interactive interview, fleet run, or installed-extension behavior was
claimed tested. Guardrail smoke checks use temporary fixtures only under clio/,
offline citation mode, and no generated-script execution.

## Extension discovery

Follow-up command: `clio-coder extensions discover ./clio --json` from the wtf-ms root.
Exit status: 0.

```json
{
  "candidates": [
    {
      "path": "/home/akougkas/iowarp/wtf-ms/clio",
      "manifestPath": "/home/akougkas/iowarp/wtf-ms/clio/clio-coder-extension.yaml",
      "manifest": {
        "manifestVersion": 1,
        "id": "wtfms",
        "name": "WTF-MS",
        "version": "0.2.0",
        "description": "Materials-science research interviews, literature synthesis, resource-aware planning, task execution, and paper handoff.",
        "resources": {
          "skills": "skills",
          "prompts": "prompts",
          "agents": "agents",
          "fleets": "fleets"
        },
        "compatibility": {
          "clio": ">=0.4.6"
        }
      },
      "valid": true,
      "diagnostics": []
    }
  ]
}
```

Stderr: (empty)

## Production resource loaders

Refreshed after the restored-executor and hardened-bridge follow-up.
Executed with existing Node/tsx and `TSX_DISABLE_CACHE=1` from the Clio Coder source checkout.
loadRecipesFromDir validates all six recipe schemas, policies and bound skills,
including the changed executor; loadSkills validates all six skill resources.
loadPromptTemplates/expandPromptTemplateInput validates all 17 prompt names and
package references, including the changed bridge. The existing fleet and README
registry example also parse. No git commands or installs were executed. Exit status: 0.

```json
{
  "recipes": [
    {
      "id": "wtfms-lab-definer",
      "boundSkillPaths": [
        "/home/akougkas/iowarp/wtf-ms/clio/skills/wtfms-lab-definer/SKILL.md"
      ],
      "tools": [
        "read",
        "context",
        "write",
        "edit",
        "grep",
        "find",
        "ls",
        "ledger",
        "limitation"
      ],
      "resultContract": {
        "kind": "mutation-report"
      }
    },
    {
      "id": "wtfms-literature-reviewer",
      "boundSkillPaths": [
        "/home/akougkas/iowarp/wtf-ms/clio/skills/wtfms-literature-reviewer/SKILL.md"
      ],
      "tools": [
        "read",
        "context",
        "write",
        "edit",
        "grep",
        "find",
        "ls",
        "web_fetch",
        "ledger",
        "limitation"
      ],
      "resultContract": {
        "kind": "mutation-report"
      }
    },
    {
      "id": "wtfms-research-explorer",
      "boundSkillPaths": [
        "/home/akougkas/iowarp/wtf-ms/clio/skills/wtfms-research-explorer/SKILL.md"
      ],
      "tools": [
        "read",
        "context",
        "write",
        "edit",
        "grep",
        "find",
        "ls",
        "ledger",
        "limitation"
      ],
      "resultContract": {
        "kind": "mutation-report"
      }
    },
    {
      "id": "wtfms-task-executor",
      "boundSkillPaths": [
        "/home/akougkas/iowarp/wtf-ms/clio/skills/wtfms-task-executor/SKILL.md"
      ],
      "tools": [
        "read",
        "context",
        "write",
        "edit",
        "grep",
        "find",
        "ls",
        "bash",
        "web_fetch",
        "ledger",
        "limitation"
      ],
      "resultContract": {
        "kind": "mutation-report"
      }
    },
    {
      "id": "wtfms-task-verifier",
      "boundSkillPaths": [
        "/home/akougkas/iowarp/wtf-ms/clio/skills/wtfms-task-verifier/SKILL.md"
      ],
      "tools": [
        "read",
        "context",
        "grep",
        "find",
        "ls",
        "ledger"
      ],
      "resultContract": {
        "kind": "mutation-report"
      }
    },
    {
      "id": "wtfms-workflow-planner",
      "boundSkillPaths": [
        "/home/akougkas/iowarp/wtf-ms/clio/skills/wtfms-workflow-planner/SKILL.md"
      ],
      "tools": [
        "read",
        "context",
        "write",
        "edit",
        "grep",
        "find",
        "ls",
        "ledger",
        "limitation"
      ],
      "resultContract": {
        "kind": "mutation-report"
      }
    }
  ],
  "recipeDiagnostics": [],
  "skills": [
    "wtfms-lab-definer",
    "wtfms-literature-reviewer",
    "wtfms-research-explorer",
    "wtfms-task-executor",
    "wtfms-task-verifier",
    "wtfms-workflow-planner"
  ],
  "skillDiagnostics": [],
  "prompts": [
    {
      "name": "wtfMS:add-task",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:archive-task",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:checkpoint",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:define-research-tasks",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:define-virtual-lab",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:execute-task",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:help",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:identify-research",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:literature-review",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:pause-research",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:progress",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:remove-task",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:resume-research",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:settings",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:status",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:upload-data",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    },
    {
      "name": "wtfMS:wtfp",
      "available": true,
      "extensionReferencesResolved": true,
      "invocationExpanded": true
    }
  ],
  "promptDiagnostics": [],
  "commandSetMatchesCanonical": true,
  "fleet": {
    "version": 4,
    "steps": [
      {
        "kind": "agent",
        "id": "execute",
        "agent": "wtfms-task-executor",
        "scope": "workspace",
        "dependencies": [],
        "writes": [
          ".research/tasks/"
        ]
      },
      {
        "kind": "agent",
        "id": "verify",
        "agent": "wtfms-task-verifier",
        "scope": "readonly",
        "dependencies": [
          "execute"
        ]
      }
    ],
    "missingVariablesRejected": true,
    "renderedVariables": true,
    "agentReferencesResolved": true
  },
  "readmeCommandRegistry": {
    "ids": [
      "wtfms-check-physics"
    ],
    "diagnostics": []
  }
}
```

## Content and guardrail checks

The guardrail smoke results below are retained from the initial port; scripts are unchanged and were not rerun in this follow-up. The handoff comparison and bridge question/choice checks were refreshed against the hardened canonical source.

```json
{
  "skillQuickValidation": [
    {
      "skill": "wtfms-lab-definer",
      "exit": 0,
      "stdout": "Skill is valid!",
      "stderr": ""
    },
    {
      "skill": "wtfms-literature-reviewer",
      "exit": 0,
      "stdout": "Skill is valid!",
      "stderr": ""
    },
    {
      "skill": "wtfms-research-explorer",
      "exit": 0,
      "stdout": "Skill is valid!",
      "stderr": ""
    },
    {
      "skill": "wtfms-task-executor",
      "exit": 0,
      "stdout": "Skill is valid!",
      "stderr": ""
    },
    {
      "skill": "wtfms-task-verifier",
      "exit": 0,
      "stdout": "Skill is valid!",
      "stderr": ""
    },
    {
      "skill": "wtfms-workflow-planner",
      "exit": 0,
      "stdout": "Skill is valid!",
      "stderr": ""
    }
  ],
  "verbatimCopies": [
    {
      "path": "resources/references/traditional-workflows.md",
      "sha256": "6954d0e990fa3e5760aa0b334f669910d5e0c8fb80dd55011aa3d98deb53a28b"
    },
    {
      "path": "resources/references/research-domains.md",
      "sha256": "0f6b7548ade7e97ffc25c057dcb43a5ad4ecc0810ac2c8c04badc9c1b5231e9e"
    },
    {
      "path": "resources/templates/VIRTUAL-LAB.md",
      "sha256": "4af9b89d6dcca79c514e23c7c9e57f3981c2674a92d7390be345ec8bf01c80b7"
    },
    {
      "path": "resources/templates/WORKFLOW.md",
      "sha256": "c94241d771afef31f2aa9bdb55f6fb9d7b8530bf811b02a1de2fbe3de04ade7b"
    },
    {
      "path": "resources/templates/RESEARCH.md",
      "sha256": "5cacea506b0d84113df8a849c669ba890dbf6f4d0b814f4378d3ff03c94cb53d"
    },
    {
      "path": "resources/templates/config.json",
      "sha256": "59c047b839be91cfc53872a05f9fdfe6f94a72293fff8a98b21b17cba4ee3c50"
    },
    {
      "path": "resources/scripts/check_physics.py",
      "sha256": "5dc34109edb436f73a3ef82ad1b04c9ae0b16446c619e4948b721feda4c9eab5"
    },
    {
      "path": "resources/scripts/check_scripts.py",
      "sha256": "98ceae8c033f50b49d691ddc64816d273cb033abcebe574c448f8d344314cbfe"
    },
    {
      "path": "resources/scripts/verify_citations.py",
      "sha256": "48d1f371bb2fa12e1c6dd1076cec38b3124bada6b86412ad2b13b13b36ef14ed"
    },
    {
      "path": "skills/wtfms-lab-definer/references/VIRTUAL-LAB.md",
      "sha256": "4af9b89d6dcca79c514e23c7c9e57f3981c2674a92d7390be345ec8bf01c80b7"
    },
    {
      "path": "skills/wtfms-lab-definer/references/research-domains.md",
      "sha256": "0f6b7548ade7e97ffc25c057dcb43a5ad4ecc0810ac2c8c04badc9c1b5231e9e"
    },
    {
      "path": "skills/wtfms-literature-reviewer/references/RESEARCH.md",
      "sha256": "5cacea506b0d84113df8a849c669ba890dbf6f4d0b814f4378d3ff03c94cb53d"
    },
    {
      "path": "skills/wtfms-literature-reviewer/references/research-domains.md",
      "sha256": "0f6b7548ade7e97ffc25c057dcb43a5ad4ecc0810ac2c8c04badc9c1b5231e9e"
    },
    {
      "path": "skills/wtfms-research-explorer/references/RESEARCH.md",
      "sha256": "5cacea506b0d84113df8a849c669ba890dbf6f4d0b814f4378d3ff03c94cb53d"
    },
    {
      "path": "skills/wtfms-research-explorer/references/config.json",
      "sha256": "59c047b839be91cfc53872a05f9fdfe6f94a72293fff8a98b21b17cba4ee3c50"
    },
    {
      "path": "skills/wtfms-research-explorer/references/research-domains.md",
      "sha256": "0f6b7548ade7e97ffc25c057dcb43a5ad4ecc0810ac2c8c04badc9c1b5231e9e"
    },
    {
      "path": "skills/wtfms-task-executor/references/VIRTUAL-LAB.md",
      "sha256": "4af9b89d6dcca79c514e23c7c9e57f3981c2674a92d7390be345ec8bf01c80b7"
    },
    {
      "path": "skills/wtfms-task-executor/references/WORKFLOW.md",
      "sha256": "c94241d771afef31f2aa9bdb55f6fb9d7b8530bf811b02a1de2fbe3de04ade7b"
    },
    {
      "path": "skills/wtfms-task-executor/references/research-domains.md",
      "sha256": "0f6b7548ade7e97ffc25c057dcb43a5ad4ecc0810ac2c8c04badc9c1b5231e9e"
    },
    {
      "path": "skills/wtfms-task-executor/references/traditional-workflows.md",
      "sha256": "6954d0e990fa3e5760aa0b334f669910d5e0c8fb80dd55011aa3d98deb53a28b"
    },
    {
      "path": "skills/wtfms-task-verifier/references/RESEARCH.md",
      "sha256": "5cacea506b0d84113df8a849c669ba890dbf6f4d0b814f4378d3ff03c94cb53d"
    },
    {
      "path": "skills/wtfms-task-verifier/references/WORKFLOW.md",
      "sha256": "c94241d771afef31f2aa9bdb55f6fb9d7b8530bf811b02a1de2fbe3de04ade7b"
    },
    {
      "path": "skills/wtfms-workflow-planner/references/RESEARCH.md",
      "sha256": "5cacea506b0d84113df8a849c669ba890dbf6f4d0b814f4378d3ff03c94cb53d"
    },
    {
      "path": "skills/wtfms-workflow-planner/references/VIRTUAL-LAB.md",
      "sha256": "4af9b89d6dcca79c514e23c7c9e57f3981c2674a92d7390be345ec8bf01c80b7"
    },
    {
      "path": "skills/wtfms-workflow-planner/references/WORKFLOW.md",
      "sha256": "c94241d771afef31f2aa9bdb55f6fb9d7b8530bf811b02a1de2fbe3de04ade7b"
    },
    {
      "path": "skills/wtfms-workflow-planner/references/traditional-workflows.md",
      "sha256": "6954d0e990fa3e5760aa0b334f669910d5e0c8fb80dd55011aa3d98deb53a28b"
    }
  ],
  "handoffPayloads": {
    "blocksCompared": 4,
    "byteIdentical": true,
    "basis": "Refreshed against hardened canonical wtfp.md during follow-up."
  },
  "interviewFidelity": [
    {
      "command": "add-task",
      "canonicalQuestionOptionLines": 3,
      "preserved": true
    },
    {
      "command": "archive-task",
      "canonicalQuestionOptionLines": 3,
      "preserved": true
    },
    {
      "command": "checkpoint",
      "canonicalQuestionOptionLines": 0,
      "preserved": true
    },
    {
      "command": "define-research-tasks",
      "canonicalQuestionOptionLines": 27,
      "preserved": true
    },
    {
      "command": "define-virtual-lab",
      "canonicalQuestionOptionLines": 15,
      "preserved": true
    },
    {
      "command": "execute-task",
      "canonicalQuestionOptionLines": 6,
      "preserved": true
    },
    {
      "command": "help",
      "canonicalQuestionOptionLines": 0,
      "preserved": true
    },
    {
      "command": "identify-research",
      "canonicalQuestionOptionLines": 18,
      "preserved": true
    },
    {
      "command": "literature-review",
      "canonicalQuestionOptionLines": 12,
      "preserved": true
    },
    {
      "command": "pause-research",
      "canonicalQuestionOptionLines": 0,
      "preserved": true
    },
    {
      "command": "progress",
      "canonicalQuestionOptionLines": 0,
      "preserved": true
    },
    {
      "command": "remove-task",
      "canonicalQuestionOptionLines": 3,
      "preserved": true
    },
    {
      "command": "resume-research",
      "canonicalQuestionOptionLines": 0,
      "preserved": true
    },
    {
      "command": "settings",
      "canonicalQuestionOptionLines": 3,
      "preserved": true
    },
    {
      "command": "status",
      "canonicalQuestionOptionLines": 0,
      "preserved": true
    },
    {
      "command": "upload-data",
      "canonicalQuestionOptionLines": 6,
      "preserved": true
    },
    {
      "command": "wtfp",
      "canonicalQuestionOptionLines": 12,
      "preserved": true
    }
  ],
  "guardrailSmoke": [
    {
      "check": "physics rejects impossible temperature",
      "expectedExit": 1,
      "actualExit": 1,
      "output": {
        "errors": [
          {
            "file": "(temporary fixture directory)/physics-bad.md",
            "line": 1,
            "rule": "temp-kelvin",
            "message": "-1 K is below absolute zero (0 K)"
          }
        ],
        "warnings": []
      },
      "stderr": ""
    },
    {
      "check": "physics accepts ordinary temperature",
      "expectedExit": 0,
      "actualExit": 0,
      "output": {
        "errors": [],
        "warnings": []
      },
      "stderr": ""
    },
    {
      "check": "script checker rejects syntax",
      "expectedExit": 1,
      "actualExit": 1,
      "output": {
        "errors": [
          {
            "file": "(temporary fixture directory)/broken.py",
            "line": 1,
            "rule": "syntax",
            "message": "SyntaxError: invalid syntax"
          }
        ],
        "warnings": []
      },
      "stderr": ""
    },
    {
      "check": "script checker accepts syntax",
      "expectedExit": 0,
      "actualExit": 0,
      "output": {
        "errors": [],
        "warnings": []
      },
      "stderr": ""
    },
    {
      "check": "offline citations stay unverified",
      "expectedExit": 0,
      "actualExit": 0,
      "output": {
        "summary": {
          "UNVERIFIABLE": 1
        },
        "results": [
          {
            "title": "Supplied materials fixture",
            "year": "2024",
            "doi": null,
            "source": "(temporary fixture directory)/source.bib",
            "raw": "@article{fixture,\n title={Supplied materials fixture},\n author={Researcher, A},\n year={2024}\n}",
            "status": "UNVERIFIABLE",
            "detail": {
              "reason": "offline mode — not resolved"
            }
          }
        ]
      },
      "stderr": ""
    }
  ],
  "temporaryFixturesRemoved": true
}
```

## Follow-up content validation

Re-read the restored executor and hardened canonical bridge. Per-type output sections and the four hardened handoff payloads were compared verbatim. Read-only detection shell examples were exercised with isolated fixtures under clio/; no recording block was executed.

```json
{
  "executorContracts": [
    {
      "type": "literature",
      "canonicalOutputContractVerbatimInSkill": true,
      "canonicalOutputContractVerbatimInRecipe": true
    },
    {
      "type": "experimental",
      "canonicalOutputContractVerbatimInSkill": true,
      "canonicalOutputContractVerbatimInRecipe": true
    },
    {
      "type": "computational",
      "canonicalOutputContractVerbatimInSkill": true,
      "canonicalOutputContractVerbatimInRecipe": true
    },
    {
      "type": "data-analysis",
      "canonicalOutputContractVerbatimInSkill": true,
      "canonicalOutputContractVerbatimInRecipe": true
    },
    {
      "type": "analytical",
      "canonicalOutputContractVerbatimInSkill": true,
      "canonicalOutputContractVerbatimInRecipe": true
    }
  ],
  "hardenedHandoffBlocks": {
    "count": 4,
    "verbatim": true
  },
  "bridgeQuestionOptionLinesPreserved": 12,
  "skillValidator": {
    "exit": 0,
    "stdout": "Skill is valid!",
    "stderr": ""
  },
  "detectionShellCases": [
    {
      "case": "blank fallback",
      "bothClaudeRootsAndGenerationsReported": true,
      "clioManifestDetected": true,
      "exit": 0
    },
    {
      "case": "tilde and spaces",
      "bothClaudeRootsAndGenerationsReported": true,
      "clioManifestDetected": true,
      "exit": 0
    }
  ],
  "singleExistingModernRecordDetected": true,
  "temporaryFixturesRemoved": true,
  "gitCommandsExecuted": false,
  "installsExecuted": false
}
```

