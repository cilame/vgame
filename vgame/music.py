import pygame

class Music:
    def __init__(self, music, volume=1):
        self.music = pygame.mixer.Sound(music)
        self.volume = volume
        self.channel = None

    def play(self, *a, **kw):
        '''
        play(loops=0, maxtime=0, fade_ms=0) -> Channel
        begin sound playback
        '''
        if self.channel and self.channel.get_busy():
            self.channel.stop()
        self.channel = self.music.play(*a, **kw)
        return self.channel

    def _get_volume(self): return self._volume
    def _set_volume(self, value): self._volume = value; self.music.set_volume(value)
    volume = property(_get_volume, _set_volume)