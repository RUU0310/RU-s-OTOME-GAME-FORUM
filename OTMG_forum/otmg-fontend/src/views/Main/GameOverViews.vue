<template>
  <div class="game-over-views">
    <div class="game-info">
      <h3 class="game-title">
        <span v-if="game.is_official" class="official-badge">官方</span>
        {{ game.name }}
      </h3>
    </div>
  </div>
</template>