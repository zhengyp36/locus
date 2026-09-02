# agent 意识层细化（第一期）—— 真实 LLM 回复 + 身份认知

> 状态：已完成并真实联调通过（见 `checkpoint-5.md`）。

> 目标：给 agent 塑基本身份（唐钰），用真实 LLM + `send_msg` 工具跑通「YZ 发消息 → 唐钰回一句话」闭环。
> 设计主文档：`agent-prototype-design.md`。前一期架子：`agent-impl.md`。代码认知：`codebase.md`。

## 目标与效果

- **离线（fake）**：注入一条 p2p 消息 → 断言 LLM 收到「身份 + 来源 + 时间」的 messages、`tools` 含 send_msg schema，工具被正确执行。
- **真实**：启动 `Agent(agent_dir)` → YZ（COGOS002:H0002）发「你好」→ 唐钰以 `send_msg(target=YZ, content=一句话)` 真实回复，飞书收到。

## 明确边界（不做）

- 不做场、元层时钟（下期）。
- 工具结果不整理/不续轮（oneshot 保持；工具成败都只是结果，本轮仅日志记录）。
- 不做群聊、通讯录转名字展示、回看历史/翻通讯录工具、主动发消息、配电脑/自创工具。
- 不碰 cog_runtime。

## 配置结构

`agent.json`（agent 根配置，相对路径基于其所在目录）：

```json
{
  "memory_dir": "memory",
  "phone_dir": "phone"
}
```

`<memory_dir>/profile.md`（YAML，pyyaml 已在依赖里，无新依赖）：

```yaml
name: 唐钰
phone_number: COGOS002:A0005
contacts:
  - name: YZ
    number: COGOS002:H0002
```

`<phone_dir>/phone.json` 由初始化自动生成，归 agent 所有。

## 文件改动

```
cogos/agent/config.py      # 新增：读 agent.json + profile.md → AgentConfig/Profile；init_phone 幂等；渲染 system prompt
cogos/agent/tools.py       # 重构：ToolRegistry + send_msg 工具（schema + 执行，失败回传结果）
cogos/agent/consciousness.py # 改：接 LmClient，组 messages，调 chat，执行 tool_calls
cogos/agent/perception.py  # 改：补消息时间（chat.history()[-1].time）
cogos/agent/app.py         # 改：Agent(agent_dir, client_factory) 组装；__main__ 用 --agent <dir>
```

依赖单向保持：`app` 组装；`perception` 回调推 `consciousness`；`consciousness` 持 `registry + lm_client + profile`；`tools` 持 phone。`config` 被 app 引用。

## 接口契约

```python
# config.py
@dataclass
class ContactInfo:
    name: str
    number: str

@dataclass
class Profile:
    name: str
    phone_number: str
    contacts: list[ContactInfo]

    def name_for(self, number: str) -> str:   # 号码→名字，未知返回号码本身

@dataclass
class AgentConfig:
    memory_dir: Path
    phone_dir: Path

def load_agent_config(agent_dir: Path) -> AgentConfig       # 读 agent.json
def load_profile(memory_dir: Path) -> Profile                # 读 profile.md
async def init_phone(phone, profile: Profile) -> None        # 幂等装卡 + 建联系人
def render_system_prompt(profile: Profile) -> str            # 身份 + 工具说明（含当前时间）

# tools.py
@dataclass
class ToolSpec:
    schema: dict        # {name, description, parameters}
    fn: Callable        # async fn(**args) -> dict（结果对象，不抛断）

class ToolRegistry:
    def __init__(self, specs: dict[str, ToolSpec]): ...
    def schemas(self, names: list[str]) -> list[dict]        # 动态组合工具集 → [{name,description,parameters}]
    async def call(self, name: str, args: dict) -> dict      # 执行并捕获异常 → {"ok":..., "reason":...}

# consciousness.py
class Consciousness:
    def __init__(self, registry, lm_client, profile, toolset_names): ...
    async def on_message(self, msg: IncomingMessage) -> None:
        messages = [{"role":"system","content": render_system_prompt(self._profile)},
                    {"role":"user","content": self._render_user(msg)}]
        resp = await self._lm_client.chat(messages, tools=self._registry.schemas(self._toolset_names))
        # 有 tool_calls：逐个 registry.call(tc["name"], tc["args"])，结果仅日志
        # 无 tool_calls 但有 content：兜底 registry.call("send_msg", {"target": msg.source, "content": text})
```

## 关键实现细节（坑，务必照做）

1. **`add_card` 不幂等**（`phone.py:115-127` 每次覆盖 card + 重建 client，旧 client 不 shutdown）。`init_phone` 必须自行判断：`any(str(c.number) == profile.phone_number for c in phone.cards())` 为 False 才 `add_card`；`get_contact(name)` 为空才 `add_contact`。
2. **消息时间可能为空**：`_make_on_msg` 用 `message.time` 写 store（可能空串/None），感知层 `chat.history()[-1].time` 补取后仍可能空。感知层如实传递，空则 `_render_user` 落「未知时间」，不阻塞。`chat.history()` 读 store（`model.py:66-80`），且 `_append_msg` 先于 `_dispatch`，取最后一条即本条。
3. **LLM 可能不调工具**：system prompt 明确要求「用 send_msg 回复」；兜底——无 `tool_calls` 但有 content，直发 `msg.source`。
4. **`send_msg` 工具 target 透传 `phone.send`**（`phone.py:193-216` 已支持名字/号码/Chat）；执行捕获异常转 `{"ok":False,"reason":...}`，不向上抛。
5. **`internal_key`**：真实模式从环境变量 `LM_INTERNAL_KEY` 读，fake 测试不读。
6. 工具集默认 `["send_msg"]`，由 `Consciousness` 构造时注入（留「工具集 ID / 工具名列表」口子）。

## 测试

- 照抄 `FakeLmClient` + `make_response`（`tests/cog_runtime/conftest.py:6-53`）进 `tests/agent/`，`make_response` 支持 `tool_calls=[{id,name,args}]`。
- 用例：
  1. `init_phone` 幂等：首次装卡 + 建联系人；二次调用不新增、不覆盖。
  2. `render_system_prompt` 含名字/手机号/联系人/时间。
  3. `ToolRegistry.schemas(["send_msg"])` 产出单工具 schema；`call` 成功/失败分别返回 `{"ok":True}` / `{"ok":False,...}`。
  4. 意识层：fake 返回 `tool_calls=[{name:"send_msg", args:{target:"YZ", content:"hi"}}]` → 断言 `send_msg` 被执行、target/content 正确。
  5. 意识层兜底：fake 返回无 tool_calls 有 content → 断言发到 `msg.source`。
- 全量回归 `python3.11 -m pytest tests/ -q` 无退化。

## 完成标准

启动 `Agent(agent_dir)`（fake）→ deliver 一条 p2p 消息 → 意识层组含身份/来源/时间的 messages 调 `chat(tools=[send_msg schema])` → 执行 send_msg 回复。pytest 通过 + 全量无回归。

## 风险评估（结论：可进入开发）

| 风险 | 级别 | 对策 |
|---|---|---|
| `add_card` 不幂等（覆盖 + 旧 client 不 shutdown） | 中 | `init_phone` 显式判断卡/联系人已存在则跳过 |
| 消息 time 可能为空 | 低 | 感知层兜底「未知时间」，不阻塞 |
| LLM 不调工具 / target 填错 | 中 | system prompt 强制 + 无 tool_calls 兜底直发 source |
| `Agent` 构造签名变化（fake/real 两条路径 + 测试） | 低 | 集中改 `app.py`，测试随契约更新 |

无阻塞性风险；坑均已在实现细节中列明，可直接进入开发。
