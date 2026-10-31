/*
 * Interactive BFS/DFS traversal demo used by the graph posts.
 *
 * Mount point in a post:
 *
 *     <div class="gt" data-graph-traversal data-mode="bfs" data-start="A"></div>
 *     <script src="/javascripts/graph-traversal.js"></script>
 *
 * navigation.instant re-executes <script> tags that live inside the page content,
 * so this file has to stay idempotent (it only ever touches its own fresh mount
 * point) and must not leave a timer running once its container has been swapped
 * away. document$ is NOT available to content scripts, so nothing here depends on
 * it.
 */
(() => {
  "use strict";

  const SVG_NS = "http://www.w3.org/2000/svg";

  /* The example graph: a "hub" graph that stays planar in this layout. */
  const GRAPH = {
    nodes: {
      A: [72, 212],
      B: [232, 112],
      C: [232, 312],
      D: [392, 52],
      E: [392, 172],
      F: [392, 252],
      G: [392, 372],
      H: [582, 212],
    },
    edges: [
      ["A", "B"], ["A", "C"],
      ["B", "D"], ["B", "E"],
      ["C", "F"], ["C", "G"],
      ["D", "H"], ["E", "H"], ["F", "H"], ["G", "H"],
    ],
  };

  /*
   * Neighbour lists are kept alphabetical so the animation visits nodes in
   * exactly the order the code samples in the post do.
   */
  const ADJACENCY = {};
  for (const node of Object.keys(GRAPH.nodes)) {
    ADJACENCY[node] = [];
  }
  for (const [u, v] of GRAPH.edges) {
    ADJACENCY[u].push(v);
    ADJACENCY[v].push(u);
  }
  for (const neighbours of Object.values(ADJACENCY)) {
    neighbours.sort();
  }

  const edgeKey = (u, v) => (u < v ? `${u}-${v}` : `${v}-${u}`);

  /*
   * Walks the graph with a queue (bfs) or a stack (dfs), marking a node as seen
   * the moment it joins the frontier, and records one entry per pop.
   */
  function traversalSteps(mode, start) {
    const store = mode === "bfs" ? "queue" : "stack";
    const past = mode === "bfs" ? "Enqueue" : "Push";
    const taken = mode === "bfs" ? "off the queue" : "off the top of the stack";
    const empty = mode === "bfs" ? "enqueued" : "pushed";

    const seen = new Set([start]);
    const frontier = [start];
    const done = [];
    const tree = new Set();
    const rejected = new Set();

    const logs = [];
    const snapshot = (current, added, fresh) => ({
      current,
      frontier: frontier.slice(),
      done: done.slice(),
      tree: [...tree],
      rejected: [...rejected],
      added: added,
      fresh: fresh,
      log: logs[logs.length - 1],
    });

    logs.push(`Seed the ${store} with ${start}, and mark it as seen straight away.`);
    const steps = [snapshot(null, [], [])];

    while (frontier.length > 0) {
      const current = mode === "bfs" ? frontier.shift() : frontier.pop();
      done.push(current);

      const added = [];
      const skipped = [];
      const fresh = [];
      for (const neighbour of ADJACENCY[current]) {
        const key = edgeKey(current, neighbour);
        if (seen.has(neighbour)) {
          skipped.push(neighbour);
          /* An edge that is already a tree edge is not a rejection. */
          if (!tree.has(key)) {
            rejected.add(key);
            fresh.push(key);
          }
          continue;
        }
        seen.add(neighbour);
        frontier.push(neighbour);
        tree.add(key);
        added.push(neighbour);
        fresh.push(key);
      }

      const head = `Take ${current} ${taken} and mark it done.`;
      let tail;
      if (added.length === 0) {
        tail = ` Every neighbour is already seen, so nothing is ${empty}.`;
      } else if (skipped.length === 0) {
        tail = ` ${past} ${added.join(", ")}.`;
      } else {
        tail = ` ${past} ${added.join(", ")}; ${skipped.join(", ")} ` +
          `${skipped.length === 1 ? "is" : "are"} already seen.`;
      }
      logs.push(head + tail);

      steps.push(snapshot(current, added, fresh));
    }

    logs.push(`The ${store} is empty, so the traversal is finished. Visit order: ${done.join(" ")}.`);
    steps.push(snapshot(null, [], []));
    return steps;
  }

  const svgEl = (name, attrs, parent) => {
    const node = document.createElementNS(SVG_NS, name);
    for (const [key, value] of Object.entries(attrs || {})) {
      node.setAttribute(key, String(value));
    }
    if (parent) {
      parent.appendChild(node);
    }
    return node;
  };

  const htmlEl = (name, className, parent, text) => {
    const node = document.createElement(name);
    if (className) {
      node.className = className;
    }
    if (text !== undefined) {
      node.textContent = text;
    }
    if (parent) {
      parent.appendChild(node);
    }
    return node;
  };

  function buildFigure(svg) {
    const edgeLayer = svgEl("g", { class: "gt-edges" }, svg);
    const edgeNodes = {};
    for (const [u, v] of GRAPH.edges) {
      const [x1, y1] = GRAPH.nodes[u];
      const [x2, y2] = GRAPH.nodes[v];
      const key = edgeKey(u, v);
      edgeNodes[key] = svgEl("line", {
        x1, y1, x2, y2,
        class: "gt-edge",
        "data-edge": key,
      }, edgeLayer);
    }

    const nodeLayer = svgEl("g", { class: "gt-nodes" }, svg);
    const nodeNodes = {};
    for (const [name, [cx, cy]] of Object.entries(GRAPH.nodes)) {
      const group = svgEl("g", { class: "gt-node", "data-node": name }, nodeLayer);
      svgEl("circle", { cx, cy, r: 24 }, group);
      svgEl("text", { x: cx, y: cy, "text-anchor": "middle", dy: "0.35em" }, group)
        .textContent = name;
      nodeNodes[name] = group;
    }
    return { edgeNodes, nodeNodes };
  }

  function buildPanel(root, mode) {
    const panel = htmlEl("div", "gt-panel", root);

    const modes = htmlEl("div", "gt-modes", panel);
    modes.setAttribute("role", "group");
    modes.setAttribute("aria-label", "Traversal algorithm");
    for (const option of ["bfs", "dfs"]) {
      const button = htmlEl("button", "gt-button gt-mode", modes, option.toUpperCase());
      button.type = "button";
      button.dataset.setMode = option;
      button.setAttribute("aria-pressed", String(option === mode));
    }

    const startBox = htmlEl("div", "gt-store", panel);
    htmlEl("span", "gt-store-label", startBox, "start");
    const select = htmlEl("select", "gt-select", startBox);
    select.setAttribute("aria-label", "Start vertex");
    for (const name of Object.keys(GRAPH.nodes)) {
      const option = htmlEl("option", null, select, name);
      option.value = name;
    }

    const frontierBox = htmlEl("div", "gt-store", panel);
    const frontierLabel = htmlEl("span", "gt-store-label", frontierBox);
    const chips = htmlEl("div", "gt-chips", frontierBox);

    const doneBox = htmlEl("div", "gt-store", panel);
    htmlEl("span", "gt-store-label", doneBox, "done");
    const doneChips = htmlEl("div", "gt-chips", doneBox);

    const logLine = htmlEl("p", "gt-log", panel);
    logLine.setAttribute("aria-live", "polite");

    const controls = htmlEl("div", "gt-controls", panel);
    const buttons = {};
    for (const [action, label] of [["play", "Play"], ["step", "Step"], ["reset", "Reset"]]) {
      const button = htmlEl("button", "gt-button", controls, label);
      button.type = "button";
      button.dataset.action = action;
      buttons[action] = button;
    }
    const counter = htmlEl("span", "gt-counter", controls);

    return { select, frontierLabel, chips, doneChips, logLine, buttons, counter };
  }

  function mount(root) {
    if (root.dataset.gtMounted === "true") {
      return;
    }
    root.dataset.gtMounted = "true";

    const readMode = () => (root.dataset.mode === "dfs" ? "dfs" : "bfs");
    const readStart = () => (root.dataset.start in GRAPH.nodes ? root.dataset.start : "A");

    const figure = htmlEl("div", "gt-figure", root);
    const svg = svgEl("svg", {
      viewBox: "0 0 654 424",
      role: "img",
      "aria-label": "Undirected graph with eight vertices labelled A to H",
    }, figure);
    const { edgeNodes, nodeNodes } = buildFigure(svg);
    const ui = buildPanel(root, readMode());

    let steps = [];
    let index = 0;
    let timer = null;

    const stop = () => {
      if (timer !== null) {
        clearTimeout(timer);
        timer = null;
      }
      ui.buttons.play.textContent = "Play";
    };

    const render = () => {
      const step = steps[index];

      for (const [name, group] of Object.entries(nodeNodes)) {
        group.classList.toggle("is-done", step.done.includes(name));
        group.classList.toggle("is-seen", step.frontier.includes(name));
        group.classList.toggle("is-current", step.current === name);
      }
      for (const [key, line] of Object.entries(edgeNodes)) {
        line.classList.toggle("is-tree", step.tree.includes(key));
        line.classList.toggle("is-rejected", step.rejected.includes(key));
        line.classList.toggle("is-fresh", step.fresh.includes(key));
      }

      const isBfs = readMode() === "bfs";
      ui.frontierLabel.textContent = isBfs ? "queue" : "stack";
      ui.chips.replaceChildren();
      for (const name of step.frontier) {
        const chip = htmlEl("span", "gt-chip", ui.chips, name);
        const isTop = isBfs
          ? step.frontier[0] === name
          : step.frontier[step.frontier.length - 1] === name;
        chip.classList.toggle("is-top", isTop);
      }
      ui.doneChips.replaceChildren();
      for (const name of step.done) {
        htmlEl("span", "gt-chip is-done", ui.doneChips, name);
      }

      ui.logLine.textContent = step.log;
      ui.counter.textContent = `step ${index} / ${steps.length - 1}`;
      ui.buttons.step.disabled = index >= steps.length - 1;
      ui.buttons.play.disabled = index >= steps.length - 1;
    };

    const reset = () => {
      stop();
      steps = traversalSteps(readMode(), readStart());
      index = 0;
      render();
    };

    const tick = () => {
      /* navigation.instant swaps the article away underneath us. */
      if (!document.body.contains(root)) {
        stop();
        return;
      }
      if (index >= steps.length - 1) {
        stop();
        return;
      }
      index += 1;
      render();
      timer = setTimeout(tick, 1100);
    };

    const play = () => {
      if (timer !== null) {
        stop();
        return;
      }
      if (index >= steps.length - 1) {
        reset();
      }
      ui.buttons.play.textContent = "Pause";
      timer = setTimeout(tick, 0);
    };

    ui.buttons.play.addEventListener("click", play);
    ui.buttons.step.addEventListener("click", () => {
      stop();
      if (index < steps.length - 1) {
        index += 1;
        render();
      }
    });
    ui.buttons.reset.addEventListener("click", reset);
    ui.select.value = readStart();
    ui.select.addEventListener("change", () => {
      root.dataset.start = ui.select.value;
      reset();
    });
    for (const button of root.querySelectorAll("[data-set-mode]")) {
      button.addEventListener("click", () => {
        root.dataset.mode = button.dataset.setMode;
        for (const other of root.querySelectorAll("[data-set-mode]")) {
          other.setAttribute("aria-pressed", String(other === button));
        }
        reset();
      });
    }

    reset();
  }

  for (const root of document.querySelectorAll("[data-graph-traversal]")) {
    mount(root);
  }

  /* Exposed so the step generator can be checked outside a browser. */
  globalThis.GraphTraversal = { GRAPH, ADJACENCY, edgeKey, traversalSteps };
})();
