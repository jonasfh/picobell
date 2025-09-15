<?php
declare(strict_types=1);

use Phinx\Migration\AbstractMigration;

final class CreateApartmentsTable extends AbstractMigration
{
    public function change(): void
    {
        $table = $this->table('apartments');
        $table
            ->addColumn('address', 'string', ['limit' => 255])
            ->addColumn('pico_serial', 'string', ['limit' => 255, 'null' => true])
            ->addColumn('created_at', 'timestamp', [
                'default' => 'CURRENT_TIMESTAMP',
            ])
            ->addColumn('modified_at', 'timestamp', [
                'default' => 'CURRENT_TIMESTAMP',
                'update' => 'CURRENT_TIMESTAMP',
            ])
            ->create();
    }
}
